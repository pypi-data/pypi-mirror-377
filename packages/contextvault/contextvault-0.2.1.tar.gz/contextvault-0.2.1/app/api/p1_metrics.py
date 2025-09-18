# app/api/p1_metrics.py
from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

from app.core.index_worker import IndexWorker

# Import module-level caches if available
try:
    from app.core.adjcache import _ADJ_CACHE  # type: ignore
except Exception:
    _ADJ_CACHE = None

try:
    from app.core.inverted_index import _INV_CACHE  # type: ignore
except Exception:
    _INV_CACHE = None

# Fallback default cache for generic usage (keeps previous behavior)
from app.core.hotcache import HotLRUCache
_default_cache = HotLRUCache(max_size=4096, default_ttl=60.0)

router = APIRouter(prefix="/metrics", tags=["metrics"])

# worker instance for status probing
_worker = IndexWorker()

class CacheClearSpec(BaseModel):
    cache_name: Optional[str] = None


# -------------------------
# Helper formatters
# -------------------------
def _safe_stats(cache) -> Dict[str, Any]:
    try:
        return cache.stats()
    except Exception:
        return {}

def _format_prom_help_type(name: str, help_text: str, metric_type: str = "gauge") -> str:
    return f"# HELP {name} {help_text}\n# TYPE {name} {metric_type}\n"

def _fmt_metric_line(name: str, value: Any, labels: Optional[Dict[str, str]] = None) -> str:
    if labels:
        label_parts = [f'{k}="{v}"' for k, v in labels.items()]
        return f'{name}{{{",".join(label_parts)}}} {value}\n'
    return f"{name} {value}\n"

def _collect_worker_prom() -> str:
    s = _worker.worker_status()
    lines = ""
    # processed_count
    lines += _format_prom_help_type("index_worker_processed_count", "Total processed jobs count")
    lines += _fmt_metric_line("index_worker_processed_count", int(s.get("processed_count", 0)))
    lines += _format_prom_help_type("index_worker_failed_count", "Total failed jobs count")
    lines += _fmt_metric_line("index_worker_failed_count", int(s.get("failed_count", 0)))
    # running
    lines += _format_prom_help_type("index_worker_running", "Worker running (1=true,0=false)")
    lines += _fmt_metric_line("index_worker_running", 1 if s.get("running") else 0)
    return lines

def _collect_cache_prom() -> str:
    parts = []
    # default cache
    def add_cache_block(cache_obj, cache_label: str):
        stats = _safe_stats(cache_obj)
        if not stats:
            return ""
        out = ""
        prefix = "cache"
        # expose hits/misses/evictions/requests/current_size/max_size
        out += _format_prom_help_type(f"{prefix}_hits", "Cache hits", "counter")
        out += _fmt_metric_line(f"{prefix}_hits", int(stats.get("hits", 0)), {"cache": cache_label})
        out += _format_prom_help_type(f"{prefix}_misses", "Cache misses", "counter")
        out += _fmt_metric_line(f"{prefix}_misses", int(stats.get("misses", 0)), {"cache": cache_label})
        out += _format_prom_help_type(f"{prefix}_evictions", "Cache evictions", "counter")
        out += _fmt_metric_line(f"{prefix}_evictions", int(stats.get("evictions", 0)), {"cache": cache_label})
        out += _format_prom_help_type(f"{prefix}_requests", "Cache requests", "counter")
        out += _fmt_metric_line(f"{prefix}_requests", int(stats.get("requests", 0)), {"cache": cache_label})
        out += _format_prom_help_type(f"{prefix}_current_size", "Cache current size (items)", "gauge")
        out += _fmt_metric_line(f"{prefix}_current_size", int(stats.get("current_size", 0)), {"cache": cache_label})
        out += _format_prom_help_type(f"{prefix}_max_size", "Cache max size (items)", "gauge")
        out += _fmt_metric_line(f"{prefix}_max_size", int(stats.get("max_size", 0)), {"cache": cache_label})
        return out

    parts.append(add_cache_block(_default_cache, "default"))
    if _ADJ_CACHE is not None:
        parts.append(add_cache_block(_ADJ_CACHE, "adj"))
    if _INV_CACHE is not None:
        parts.append(add_cache_block(_INV_CACHE, "inv"))
    return "\n".join([p for p in parts if p])

# -------------------------
# Endpoints
# -------------------------
@router.get("/cache", summary="Get hot-cache stats (aggregated default/adj/inv)")
def cache_stats():
    resp = {
        "ok": True,
        "default_cache": _default_cache.stats(),
        "adj_cache": _ADJ_CACHE.stats() if _ADJ_CACHE is not None else None,
        "inverted_cache": _INV_CACHE.stats() if _INV_CACHE is not None else None,
    }
    return JSONResponse(resp)

@router.get("/cache/adj", summary="Get adjacency cache stats")
def cache_adj_stats():
    if _ADJ_CACHE is None:
        raise HTTPException(status_code=404, detail="adjacency cache not available")
    return {"ok": True, "cache": _ADJ_CACHE.stats()}

@router.get("/cache/inverted", summary="Get inverted-index cache stats")
def cache_inv_stats():
    if _INV_CACHE is None:
        raise HTTPException(status_code=404, detail="inverted cache not available")
    return {"ok": True, "cache": _INV_CACHE.stats()}

@router.post("/cache/clear", summary="Clear hot-cache")
def cache_clear(spec: CacheClearSpec = Body(None)):
    # clear default cache
    _default_cache.clear()
    # optionally clear named caches
    if spec and spec.cache_name:
        cn = spec.cache_name.lower()
        if cn == "adj" and _ADJ_CACHE is not None:
            _ADJ_CACHE.clear()
        elif cn == "inv" and _INV_CACHE is not None:
            _INV_CACHE.clear()
    return {"ok": True, "cleared": True}

@router.get("/worker", summary="Index worker status")
def worker_status():
    try:
        return {"ok": True, "status": _worker.worker_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", summary="Quick health check")
def health():
    return {"ok": True, "status": "ok"}

@router.get("/text", response_class=PlainTextResponse, summary="Prometheus-style metrics text")
def metrics_text():
    """
    Return a Prometheus-compatible plaintext exposition of selected metrics:
      - index_worker_processed_count, index_worker_failed_count, index_worker_running
      - cache_* for default/adj/inv caches: hits, misses, evictions, requests, current_size, max_size
    """
    lines = []
    # timestamp
    lines.append(f"# Generated at {datetime.utcnow().isoformat()}Z\n")
    # worker metrics
    try:
        lines.append(_collect_worker_prom())
    except Exception:
        # fallback: emit nothing
        pass
    # caches
    try:
        lines.append(_collect_cache_prom())
    except Exception:
        pass

    body = "\n".join([l for l in lines if l])
    # Prometheus expects text/plain; version=0.0.4 typically
    return PlainTextResponse(content=body, media_type="text/plain; version=0.0.4")
