"""Prometheus metrics middleware for FastAPI applications."""

import time
from typing import Any, MutableMapping, Union

from prometheus_client import REGISTRY, Counter, Histogram
from starlette.types import ASGIApp, Receive, Scope, Send

# Global metrics for all services
REQUEST_COUNT: Union[Counter, Any]
REQUEST_LATENCY: Union[Histogram, Any]

# Note: Prometheus metrics are singleton by nature - once created, they persist
# in the registry. This is intentional behavior for production use.
try:
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["service", "method", "path", "status"],
    )

    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency",
        ["service", "method", "path"],
    )
except ValueError as exc:
    # Metrics already exist - find and reuse them
    # This can happen during development with module reloads
    _temp_count: Any = None
    _temp_latency: Any = None

    for collector in list(REGISTRY._collector_to_names.keys()):  # pylint: disable=protected-access
        if hasattr(collector, "_name"):  # pylint: disable=protected-access
            name = getattr(collector, "_name", None)  # pylint: disable=protected-access
            if name == "http_requests_total":
                _temp_count = collector
            elif name == "http_request_duration_seconds":
                _temp_latency = collector

    # Ensure we have valid metrics
    if _temp_count is None or _temp_latency is None:
        raise RuntimeError(
            "Prometheus metrics initialization failed. "
            "This may happen during development with frequent module reloads. "
            "Please restart the Python process."
        ) from exc

    REQUEST_COUNT = _temp_count
    REQUEST_LATENCY = _temp_latency


class PrometheusMiddleware:
    """ASGI middleware to collect Prometheus metrics for HTTP requests.

    This middleware tracks:
    - Request count by service, method, path, and status code
    - Request latency by service, method, and path

    Usage:
        app.add_middleware(PrometheusMiddleware, service_name="my-service")
    """

    def __init__(self, app: ASGIApp, service_name: str) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application to wrap
            service_name: Name of the service for metrics labeling
        """
        self.app = app
        self.service = service_name

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Process HTTP requests and collect metrics."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"]
        path = scope.get("path", "")
        start = time.perf_counter()
        status_code_holder: dict[str, int] = {"code": 0}

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            """Wrapper to capture response status code."""
            if message["type"] == "http.response.start":
                status_code_holder["code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.perf_counter() - start
            REQUEST_LATENCY.labels(self.service, method, path).observe(
                duration
            )
            REQUEST_COUNT.labels(
                self.service, method, path, str(status_code_holder["code"])
            ).inc()
