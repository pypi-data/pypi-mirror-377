from datetime import datetime, timezone
import pytz

def px(n: int) -> str:
    return f"{int(n)}px"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def to_local_str(iso_str: str | None, tz_name: str) -> str:
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if not dt.tzinfo:
            from datetime import timezone as tz
            dt = dt.replace(tzinfo=tz.utc)
        return dt.astimezone(pytz.timezone(tz_name)).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return str(iso_str)
 

# dataset_dashboard/constants.py
from typing import Tuple, Dict

# exact order (worst → best). keep 'other' at the end.
JOB_STATUS_ORDER = [
    "failed", "overdue", "manual", "retrying", "running",
    "allocated", "queued", "waiting", "succeeded", "other"
]

JOB_COLORS: Dict[str, str] = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "allocated": "#7759C2",
    "queued":    "#6C757D",
    "succeeded": "#009E73",
    "other":     "#999999",
}

JOB_SCORES: Dict[str, float] = {
    "failed": -1.0, "overdue": -0.8, "retrying": -0.3, "running": 0.5,
    "allocated": 0.2, "queued": 0.1, "waiting": 0.0, "manual": 0.2,
    "succeeded": 1.0, "other": 0.0,
}

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}

# --- NEW: light-touch canonicalization map (all keys *lowercase*) ---
# We only map common variants; anything else falls back to 'other' safely.
STATUS_CANON: Dict[str, str] = {
    # success
    "success": "succeeded", "succeed": "succeeded", "ok": "succeeded", "done": "succeeded",
    # failure
    "fail": "failed", "error": "failed", "failed_job": "failed",
    # overdue / timeout
    "timeout": "overdue", "time_out": "overdue", "over_due": "overdue",
    # retrying
    "retry": "retrying", "retried": "retrying",
    # running
    "in_progress": "running", "processing": "running",
    # waiting / pending
    "pend": "waiting", "pending": "waiting",
    # queued / allocated
    "queue": "queued", "queued_up": "queued",
    "alloc": "allocated", "allocated_job": "allocated",
    # manual / paused
    "pause": "manual", "paused": "manual",
    # empty/unknown → handled in store as 'other'
}

from typing import Dict, Optional, Iterable, Union, List
from ..constants import JOB_STATUS_ORDER

def _norm(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip().lower()
    return None if s in ("", "all") else s

def count_statuses(
    store: dict,
    owner: Optional[str] = None,
    mode: Optional[str] = None,
    stage: Union[None, str, Iterable[str]] = None,
) -> Dict[str, int]:
    """
    Aggregate status counts with optional filters.

    Args
    ----
    store : dashboard state dict
    owner : owner key (case-insensitive). "All"/""/None means no filter.
    mode  : mode key (case-insensitive).  "All"/""/None means no filter.
    stage : None → all stages; str → that stage; Iterable[str] → any of those.

    Returns
    -------
    dict[str,int] for *every* status in JOB_STATUS_ORDER. Unknown statuses are
    counted into "other" if present in JOB_STATUS_ORDER; otherwise ignored.
    """
    want_owner = _norm(owner)
    want_mode  = _norm(mode)

    # normalize stages into a set (lowercased) or None for "all"
    if stage is None:
        want_stages = None
    elif isinstance(stage, str):
        want_stages = {stage.strip().lower()}
    else:
        want_stages = {str(s).strip().lower() for s in stage}

    # init result with zeros for all known statuses
    out = {s: 0 for s in JOB_STATUS_ORDER}
    has_other = "other" in out

    jobs = store.get("jobs", {})
    for own_key, o_map in jobs.items():
        if want_owner and own_key != want_owner:
            continue
        for mode_key, m_map in o_map.items():
            if want_mode and mode_key != want_mode:
                continue
            for _dn, d_map in m_map.items():
                for stg, leaf in d_map.items():
                    stg_key = stg.lower()
                    if want_stages is not None and stg_key not in want_stages:
                        continue
                    counts = (leaf or {}).get("counts") or {}
                    for status, val in counts.items():
                        s_key = str(status).lower()
                        v = int(val or 0)
                        if s_key in out:
                            out[s_key] += v
                        elif has_other:
                            out["other"] += v
                        # else: drop unknowns silently

    return out