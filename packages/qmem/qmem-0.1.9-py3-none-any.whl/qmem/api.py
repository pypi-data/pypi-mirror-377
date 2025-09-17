from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Union

from qdrant_client import models as qmodels

from .client import QMem
from .config import CONFIG_PATH, QMemConfig
from .schemas import IngestItem, RetrievalResult

__all__ = [
    "create",
    "ingest",
    "ingest_from_file",
    "retrieve",
    "retrieve_by_filter",
    "mongo",  # mirror existing collection -> MongoDB (Qdrant or Chroma backend)
]

# -----------------------------
# Internals
# -----------------------------

_DISTANCE: Dict[str, qmodels.Distance] = {
    "cosine": qmodels.Distance.COSINE,
    "dot": qmodels.Distance.DOT,
    "euclid": qmodels.Distance.EUCLID,
}


def _normalize_payload_keys(keys: Optional[Sequence[str]]) -> Optional[Set[str]]:
    """Normalize a sequence of payload keys to a unique, trimmed set (or None)."""
    if keys is None:
        return None
    return {k.strip() for k in keys if k and k.strip()}


def _items(records: Iterable[dict], embed_field: Optional[str]) -> List[IngestItem]:
    """
    Convert raw dict records into IngestItem objects.
    """
    items: List[IngestItem] = []
    for d in records:
        known = dict(d)
        known["embed_field"] = embed_field
        if embed_field and embed_field in d:
            known[embed_field] = d[embed_field]
        for k in ("query", "response", "sql_query", "doc_id", "graph", "tags"):
            if k in d:
                known[k] = d[k]
        known.pop("extra", None)
        items.append(IngestItem(**known))
    return items


def _read_json_or_jsonl(path: Union[str, Path]) -> List[dict]:
    """Read .jsonl or .json into a list of dicts."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No such file: {p}")

    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".jsonl":
        return [json.loads(ln) for ln in text.splitlines() if ln.strip()]
    obj = json.loads(text)
    return obj if isinstance(obj, list) else [obj]


# -----------------------------
# Public API (low-level core)
# -----------------------------

def create(
    collection: str,
    *,
    cfg: Optional[QMemConfig] = None,
    dim: Optional[int] = None,
    distance: Union[str, qmodels.Distance] = "cosine",
) -> None:
    cfg = cfg or QMemConfig.load(CONFIG_PATH)
    if dim is None:
        vec_dim = cfg.embed_dim or 1536
    else:
        vec_dim = int(dim)
        if cfg.embed_dim != vec_dim:
            cfg.embed_dim = vec_dim
            cfg.save(CONFIG_PATH)
    q = QMem(cfg, collection=collection)
    backend = getattr(q, "_backend", "qdrant")
    try:
        q.ensure_collection(create_if_missing=False)
        return
    except Exception:
        pass
    if backend == "qdrant":
        if isinstance(distance, str):
            key = distance.strip().lower()
            if key not in _DISTANCE:
                raise ValueError(f"Invalid distance: {distance!r}. Choose from: {', '.join(_DISTANCE)}")
            dist = _DISTANCE[key]
        else:
            dist = distance
        q.ensure_collection(create_if_missing=True, distance=dist, vector_size=vec_dim)
    else:
        q.ensure_collection(create_if_missing=True)


def ingest(
    collection: str,
    records: Iterable[dict],
    *,
    embed_field: Optional[str],
    cfg: Optional[QMemConfig] = None,
    payload_keys: Optional[Sequence[str]] = None,
    include_embed_in_payload: bool = True,
) -> int:
    if not embed_field:
        raise ValueError("embed_field is required")
    cfg = cfg or QMemConfig.load(CONFIG_PATH)
    q = QMem(cfg, collection=collection)
    try:
        q.ensure_collection(create_if_missing=False)
    except Exception as e:
        raise RuntimeError(f"No such collection: {collection}") from e
    items = _items(records, embed_field)
    return q.ingest(
        items,
        payload_keys=_normalize_payload_keys(payload_keys),
        include_embed_in_payload=include_embed_in_payload,
    )


def ingest_from_file(
    collection: str,
    path: Union[str, Path],
    *,
    embed_field: Optional[str],
    cfg: Optional[QMemConfig] = None,
    payload_keys: Optional[Sequence[str]] = None,
    include_embed_in_payload: bool = True,
) -> int:
    if not embed_field:
        raise ValueError("embed_field is required")
    records = _read_json_or_jsonl(path)
    return ingest(
        collection,
        records,
        embed_field=embed_field,
        cfg=cfg,
        payload_keys=payload_keys,
        include_embed_in_payload=include_embed_in_payload,
    )


def retrieve(
    collection: str,
    query: str,
    *,
    k: int = 5,
    cfg: Optional[QMemConfig] = None,
) -> List[RetrievalResult]:
    if not query:
        raise ValueError("query is required")
    cfg = cfg or QMemConfig.load(CONFIG_PATH)
    q = QMem(cfg, collection=collection)
    try:
        q.ensure_collection(create_if_missing=False)
    except Exception as e:
        raise RuntimeError(f"No such collection: {collection}") from e
    return q.search(query, top_k=k)


def retrieve_by_filter(
    collection: str,
    *,
    filter: Union[dict, qmodels.Filter],
    k: int = 100,
    query: Optional[str] = None,
    cfg: Optional[QMemConfig] = None,
) -> List[RetrievalResult]:
    cfg = cfg or QMemConfig.load(CONFIG_PATH)
    q = QMem(cfg, collection=collection)
    try:
        q.ensure_collection(create_if_missing=False)
    except Exception as e:
        raise RuntimeError(f"No such collection: {collection}") from e
    if query:
        return q.search_filtered(query, top_k=k, query_filter=filter)
    results, _ = q.scroll_filter(query_filter=filter, limit=k)
    return results


# -----------------------------
# Programmatic Mongo mirror
# -----------------------------

def mongo(
    *,
    collection_name: str,
    fields: Optional[Sequence[str]] = None,
    mongo_uri: str = "mongodb://127.0.0.1:27017",
    mongo_db: str = "qmem",
    mongo_collection: Optional[str] = None,
    batch_size: int = 1000,
    max_docs: Optional[int] = None,
    cfg: Optional[QMemConfig] = None,
) -> int:
    """
    Mirror an existing collection's payloads into MongoDB (supports Qdrant and Chroma backends).
    """
    cfg = cfg or QMemConfig.load(CONFIG_PATH)
    q = QMem(cfg, collection=collection_name)
    try:
        q.ensure_collection(create_if_missing=False)
    except Exception as e:
        raise RuntimeError(f"No such collection: {collection_name}") from e
    mongo_keys: Optional[Set[str]] = set(fields) if fields else None
    coll = mongo_collection or collection_name
    return q.mirror_to_mongo(
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        mongo_coll=coll,
        mongo_keys=mongo_keys,
        batch_size=batch_size,
        max_docs=max_docs,
    )