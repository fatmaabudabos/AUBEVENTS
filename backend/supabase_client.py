from __future__ import annotations

from functools import lru_cache
from typing import Optional

from django.conf import settings

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - handled via runtime config
    Client = None  # type: ignore
    create_client = None  # type: ignore


@lru_cache(maxsize=1)
def get_supabase_client() -> Optional["Client"]:
    """Return a cached Supabase client or ``None`` when not configured."""
    url = getattr(settings, "SUPABASE_URL", None)
    key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)
