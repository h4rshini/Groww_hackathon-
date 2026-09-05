from fastapi import APIRouter, Depends

from .deps import get_current_user
from .fetcher import FetchError, search_symbols

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str, user=Depends(get_current_user)):
    q = q.strip()
    if not q:
        return []
    try:
        return search_symbols(q)
    except FetchError:
        return []  # best-effort: an empty list is fine if the provider hiccups
