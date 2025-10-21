# app/src/event_analyzer.py
from collections import Counter
from typing import Any, Dict, Iterable, List

try:
    # optional import; we only use it for isinstance checks
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover
    BaseModel = object  # fallback if pydantic not present in this scope


class EventAnalyzer:
    @staticmethod
    def _identity(joiner: Dict[str, Any]) -> str:
        """
        Unique identity for a joiner.
        Prefer email (case-insensitive). Fallback to name.
        """
        email = (joiner or {}).get("email")
        name = (joiner or {}).get("name")
        if email:
            return email.strip().lower()
        return (name or "").strip()

    @classmethod
    def get_joiners_multiple_meetings_method(
        cls, events: Iterable[Any]
    ) -> List[str]:
        """
        Return identities for joiners who appear in >= 2 different events.
        Accepts events as dicts or Pydantic models.
        """
        counts = Counter()

        for ev in events or []:
            # normalise event to dict
            if isinstance(ev, dict):
                ev_dict = ev
            elif isinstance(ev, BaseModel):
                # pydantic v2 has model_dump, v1 has dict()
                ev_dict = ev.model_dump() if hasattr(ev, "model_dump") else ev.dict()
            else:
                # unknown type; skip safely
                continue

            # collect unique joiners for this single event to avoid double-count within one event
            per_event_ids = set()
            for j in (ev_dict.get("joiners") or []):
                if isinstance(j, dict):
                    ident = cls._identity(j)
                    if ident:
                        per_event_ids.add(ident)
            for ident in per_event_ids:
                counts[ident] += 1

        return [ident for ident, c in counts.items() if c >= 2]
