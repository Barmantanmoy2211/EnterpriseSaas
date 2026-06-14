from typing import Any

from fastapi import APIRouter, Depends, Query

from app.analytics.service import AnalyticsOverview, AnalyticsService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(user=Depends(require_permission("analytics", "read"))):
    return await AnalyticsService.get_overview(str(user.tenant_id))


@router.get("/trends")
async def get_entity_trends(
    entity_type: str = Query("employee"),
    days: int = Query(30, ge=1, le=365),
    user=Depends(require_permission("analytics", "read")),
) -> dict[str, Any]:
    return await AnalyticsService.get_entity_trends(str(user.tenant_id), entity_type, days)
