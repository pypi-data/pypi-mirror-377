"""Common FastAPI application factory for all services."""

from dataclasses import dataclass
from typing import Callable, Dict, Optional, cast

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from mysingle.config import settings
from mysingle.health import create_health_routers
from mysingle.middleware import AuthMiddleware, PrometheusMiddleware


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for each route based on its tags and name."""
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


@dataclass
class AppConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for FastAPI application creation."""

    service_name: str
    service_version: str = "0.1.0"
    title: Optional[str] = None
    description: Optional[str] = None
    enable_auth: bool = True
    enable_metrics: bool = True
    enable_rbac: bool = False  # RBAC 미들웨어 활성화 여부
    rbac_protected_paths: Optional[dict[str, dict[str, str]]] = (
        None  # RBAC 보호 경로
    )
    rbac_enable_path_based_check: bool = True  # 경로 기반 자동 권한 확인
    public_paths: Optional[list[str]] = None
    cors_origins: Optional[list[str]] = None
    lifespan: Optional[Callable] = None


def create_fastapi_app_with_config(config: AppConfig) -> FastAPI:
    """Create a standardized FastAPI application with common middleware and routes.

    Args:
        config: Application configuration containing all necessary settings

    Returns:
        Configured FastAPI application
    """
    # Extract configuration values
    app_title = (
        config.title
        or f"MySingle {config.service_name.replace('_', ' ').title()}"
    )
    app_description = (
        config.description or f"{config.service_name} for MySingle platform"
    )

    # Default public paths
    default_public_paths = [
        "/health",
        "/version",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    if config.enable_metrics:
        default_public_paths.append("/metrics")
    final_public_paths = config.public_paths or default_public_paths

    # Check if we're in development
    is_development = (
        not hasattr(settings, "ENVIRONMENT")
        or settings.ENVIRONMENT == "development"
        or settings.ENVIRONMENT == "local"
    )

    # Create FastAPI app
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=config.service_version,
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=config.lifespan,
        docs_url="/docs" if is_development else None,
        redoc_url="/redoc" if is_development else None,
        openapi_url="/openapi.json" if is_development else None,
    )

    # Add CORS middleware
    if config.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add authentication middleware (conditionally)
    auth_condition = config.enable_auth and (
        not hasattr(settings, "ENVIRONMENT")
        or settings.ENVIRONMENT not in ["development", "local"]
    )
    if auth_condition:
        app.add_middleware(
            AuthMiddleware,
            public_paths=final_public_paths,
        )

    # Add RBAC middleware (conditionally)
    if config.enable_rbac:
        from mysingle.middleware.rbac_middleware import (
            RBACMiddleware,
            RBACMiddlewareConfig,
        )

        # RBAC 설정 생성
        rbac_config = {
            "protected_paths": config.rbac_protected_paths or {},
            "enable_path_based_check": config.rbac_enable_path_based_check,
            "excluded_paths": set(final_public_paths),
        }

        # 서비스별 기본 보호 경로가 없으면 생성
        if not config.rbac_protected_paths:
            rbac_config["protected_paths"] = (
                RBACMiddlewareConfig.create_service_config(
                    service_name=config.service_name,
                    resources=["items", "users", "settings"],  # 기본 리소스
                )
            )

        app.add_middleware(
            RBACMiddleware,
            rbac_service_url=None,  # 기본값 사용
            protected_paths=cast(
                Optional[Dict[str, Dict[str, str]]],
                rbac_config.get("protected_paths"),
            ),
            excluded_paths=cast(
                Optional[set], rbac_config.get("excluded_paths")
            ),
            enable_path_based_check=bool(
                rbac_config.get("enable_path_based_check", False)
            ),
            enable_batch_optimization=True,  # 기본값
        )

    # Add metrics middleware
    if config.enable_metrics:
        app.add_middleware(
            PrometheusMiddleware, service_name=config.service_name
        )

    # Add health routes
    _, public_health_router = create_health_routers(
        config.service_name, config.service_version, config.enable_metrics
    )
    app.include_router(public_health_router)

    return app


def create_fastapi_app(
    service_name: str,
    service_version: str = "0.1.0",
    title: Optional[str] = None,
    description: Optional[str] = None,
    enable_auth: bool = True,
    enable_metrics: bool = True,
    enable_rbac: bool = True,
    rbac_protected_paths: Optional[dict[str, dict[str, str]]] = None,
    rbac_enable_path_based_check: bool = True,
    public_paths: Optional[list[str]] = None,
    cors_origins: Optional[list[str]] = None,
    lifespan: Optional[Callable] = None,
) -> FastAPI:
    """Create a FastAPI application with RBAC middleware enabled.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        title: Custom title for the API documentation
        description: Custom description for the API
        enable_auth: Whether to enable authentication middleware
        enable_metrics: Whether to enable metrics collection
        enable_rbac: Whether to enable RBAC middleware
        rbac_protected_paths: Dictionary of protected paths and their permissions
        rbac_enable_path_based_check: Enable automatic path-based permission checks
        public_paths: List of public paths that don't require authentication
        cors_origins: List of allowed CORS origins
        lifespan: Optional lifespan context manager

    Returns:
        Configured FastAPI application with RBAC
    """
    config = AppConfig(
        service_name=service_name,
        service_version=service_version,
        title=title,
        description=description,
        enable_auth=enable_auth,
        enable_metrics=enable_metrics,
        enable_rbac=enable_rbac,
        rbac_protected_paths=rbac_protected_paths,
        rbac_enable_path_based_check=rbac_enable_path_based_check,
        public_paths=public_paths,
        cors_origins=cors_origins,
        lifespan=lifespan,
    )
    return create_fastapi_app_with_config(config)
