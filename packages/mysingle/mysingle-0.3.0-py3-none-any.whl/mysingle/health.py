"""Common health check endpoints for all services."""

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def _get_guardrails():
    """지연 import로 순환 import 방지"""
    from .guardrails.auth.dependencies import get_tenant_id, require_permission

    return require_permission, get_tenant_id


def create_health_routers(
    service_name: str,
    service_version: str = "0.1.0",
    enable_metrics: bool = True,
) -> tuple[APIRouter, APIRouter]:
    """Create authenticated and public health check routers.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        enable_metrics: Whether to include metrics endpoint

    Returns:
        Tuple of (authenticated_router, public_router)
    """
    # 지연 import로 순환 import 방지
    authorize, get_tenant_id = _get_guardrails()

    # Router used for versioned API paths (e.g. ``/api/v1/health/``)
    authenticated_router = APIRouter(
        dependencies=[Depends(get_tenant_id), Depends(authorize)]
    )

    # Router for top-level service metadata endpoints (``/health`` and ``/version``)
    public_router = APIRouter()

    @authenticated_router.get("/")
    async def api_health() -> dict[str, str]:
        """Return service health status for API routes."""
        return {"status": "ok"}

    @public_router.get("/health")
    async def health() -> dict[str, str]:
        """Return basic service health information."""
        return {"status": "ok", "service": service_name}

    @public_router.get("/version")
    async def version() -> dict[str, str]:
        """Return service version information."""
        return {"service": service_name, "version": service_version}

    if enable_metrics:

        @public_router.get("/metrics")
        async def metrics() -> Response:
            """Return Prometheus metrics."""
            data = generate_latest()
            return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return authenticated_router, public_router


# Backward compatibility exports
def create_public_health_router(
    service_name: str,
    service_version: str = "0.1.0",
    enable_metrics: bool = True,
) -> APIRouter:
    """Create a public health router (backward compatibility)."""
    _, public_router = create_health_routers(
        service_name, service_version, enable_metrics
    )
    return public_router


def create_authenticated_health_router() -> APIRouter:
    """Create an authenticated health router (backward compatibility)."""
    authenticated_router, _ = create_health_routers("unknown")
    return authenticated_router
