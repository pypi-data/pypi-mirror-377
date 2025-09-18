"""Common configurations for services"""

from typing import Annotated, Any, Literal, Self

from pydantic import BeforeValidator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS configuration."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class CommonSettings(BaseSettings):
    """Configuration for services"""

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.development"],
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True,
        validate_default=True,
    )

    # ==============================================================================
    # 공통 설정 (mapping w/ .env)
    # ==============================================================================

    # 🏗️ PROJECT SETTINGS (공통)
    PROJECT_NAME: str = "your_project_name"
    DOMAIN: str = "yourdomain.com"

    # ⚡ PERFORMANCE SETTINGS (공통)
    CACHE_TTL_SECONDS: int = 300
    DB_CONNECTION_POOL_SIZE: int = 5
    API_RATE_LIMIT: int = 1000
    REQUEST_TIMEOUT_SECONDS: int = 30
    BATCH_PROCESSING_ENABLED: bool = True
    BATCH_MAX_WORKERS: int = 2

    # 📊 AUDIT & LOGGING (공통)
    LOG_FORMAT: str = "json"
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90

    # 🕐 SESSION MANAGEMENT (공통)
    SESSION_TIMEOUT_MINUTES: int = 30
    SESSION_EXTEND_ON_ACTIVITY: bool = True

    # ⚙️ FEATURE FLAGS (공통)
    FEATURE_AI_ENABLED: bool = True
    FEATURE_ADVANCED_ANALYTICS: bool = False
    FEATURE_MULTI_CURRENCY: bool = True
    FEATURE_CASHBOOK: bool = True
    FEATURE_OAUTH_LOGIN: bool = True

    # 🌱 DEVELOPMENT SEED DATA (개발용)
    CREATE_INITIAL_TENANTS: bool = False
    CREATE_TEST_USERS: bool = False
    AUTO_SEED_MASTER_DATA: bool = False
    SEED_DATA_TENANT_COUNT: int = 3

    # 🤖 AI GATEWAY SETTINGS (공통)
    LLM_PROVIDER: str = "openai"
    LLM_API_BASE: str = "https://api.openai.com/v1"
    LLM_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    COST_BUDGET_PER_DAY: float = 100.0
    MAX_TOKENS: int = 4000
    MAX_RETRIES: int = 3
    ALLOW_TOOL_CALLS: bool = True

    QDRANT_URL: str = "http://qdrant:6333"
    KAFKA_BROKERS: str = "redpanda:9092"

    # ==============================================================================
    # 환경별 차등 설정
    # ==============================================================================

    # IDENTIFY ENVIRONMENT AND DEBUGGING
    ENVIRONMENT: Literal["development", "local", "staging", "production"] = (
        "development"
    )
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # 👤 SUPERUSER CREDENTIALS (MongoDB, Redis, MinIO)
    INFRA_SERVICE_SUPERUSER_ID: str = "admin"
    INFRA_SERVICE_SUPERUSER_PASSWORD: str = "change-this-password"
    FIRST_SUPER_USER_EMAIL: str = "your_email@example.com"
    FIRST_SUPER_USER_PASSWORD: str = "change-this-admin-password"

    # 🌐 SERVICE URLS (환경별)
    TENANT_SERVICE_URL: str = "http://tenant.localhost"
    IAM_SERVICE_URL: str = "http://iam.localhost"
    RBAC_SERVICE_URL: str = "http://rbac.localhost"
    TEMPLATE_CATALOG_URL: str = "http://template.localhost"
    OBJECT_STORAGE_SERVICE_URL: str = "http://storage.localhost"
    I18N_SERVICE_URL: str = "http://i18n.localhost"

    LEDGER_SERVICE_URL: str = "http://ledger.localhost"

    AI_GATEWAY_URL: str = "http://ai-gw.localhost"
    EMBEDDING_WORKER_URL: str = "http://ai-ew.localhost"
    EVALUATION_SERVICE_URL: str = "http://ai-eval.localhost"

    # 🔐 SECURITY SETTINGS (환경별)
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key"
    JWT_REFRESH_SECRET_KEY: str = "change-this-jwt-refresh-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    # CORS 설정
    BACKEND_CORS_ORIGINS: Annotated[
        list[str] | str, BeforeValidator(parse_cors)
    ] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    @property
    def all_cors_origins(self) -> list[str]:
        """All CORS origins."""
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ]

    # 🗄️ DATABASE SETTINGS (환경별)
    MONGODB_SERVER: str = "localhost:27017"
    REDIS_HOST: str = "localhost:6379"
    # 통합 인프라 서비스 관리자 계정 지원

    @property
    def redis_url(self) -> str:
        """Redis connection URL using unified infrastructure admin account."""
        # 통합 관리자 계정 비밀번호를 우선 사용
        redis_password = self.INFRA_SERVICE_SUPERUSER_PASSWORD
        if redis_password:
            return f"redis://default:{redis_password}@{self.REDIS_HOST}"
        return f"redis://{self.REDIS_HOST}"

    # 📧 SMTP SETTINGS (환경별)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            object.__setattr__(self, "EMAILS_FROM_NAME", self.PROJECT_NAME)
        return self

    @property
    def emails_enabled(self) -> bool:
        """Confirms if email settings are correctly configured."""
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # 🔔 WEBHOOKS & NOTIFICATIONS (환경별 차등적용)
    NOTIFICATION_WEBHOOK_URL: str | None = None
    SLACK_WEBHOOK_URL: str | None = None

    # 💱 EXTERNAL APIS (환경별 차등적용)
    EXCHANGE_RATE_API_KEY: str | None = None
    EXCHANGE_RATE_API_URL: str = "https://api.exchangerate-api.com/v4/latest"


settings = CommonSettings()
