from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.search.schemas import IndexDocumentRequest, SearchResponse, SearchResult
from app.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(require_permission("search", "read")),
):
    return await SearchService.search(str(user.tenant_id), q, limit)


@router.post("/index", response_model=SearchResult, status_code=status.HTTP_201_CREATED)
async def index_document(
    data: IndexDocumentRequest,
    user=Depends(require_permission("search", "manage")),
):
    return await SearchService.index(str(user.tenant_id), data)


@router.post("/reindex", status_code=status.HTTP_200_OK)
async def reindex_tenant(user=Depends(require_permission("search", "manage"))):
    count = await SearchService.reindex_tenant(str(user.tenant_id))
    return {"indexed": count}
