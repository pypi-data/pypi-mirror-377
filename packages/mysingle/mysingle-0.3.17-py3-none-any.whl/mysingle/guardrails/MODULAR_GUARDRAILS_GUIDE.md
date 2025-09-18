# 모듈형 가드레일 시스템 가이드

- 문서버전: `V.1.0`
- 업데이트일시: `2025년 9월 16일`
- 아키텍처: `모듈형 분리 구조`

## 🎯 개요

MySingle 플랫폼의 **모듈형 가드레일 시스템**은 보안, 권한 관리, Rate Limiting, PII 보호, 감사 로깅을 목적별로 분리된 모듈로 제공합니다.

각 모듈은 독립적으로 사용할 수 있으며, 필요에 따라 조합하여 사용할 수 있습니다.

## 🏗️ 모듈형 아키텍처

### 디렉토리 구조

```
py_common/guardrails/
├── __init__.py                 # 모듈 통합 인터페이스
├── core/                       # 핵심 설정 및 베이스 클래스
│   ├── __init__.py
│   ├── config.py              # GuardrailConfig
│   └── base.py                # BaseGuardrail 추상 클래스
├── auth/                       # 권한 확인 모듈
│   ├── __init__.py
│   ├── permission_checker.py  # 권한 확인 로직
│   └── dependencies.py        # FastAPI 의존성들
├── rate_limiting/              # Rate Limiting 모듈
│   ├── __init__.py
│   ├── limiter.py             # Rate Limiting 로직
│   └── store.py               # Rate Limit 저장소
├── privacy/                    # PII 보호 모듈
│   ├── __init__.py
│   ├── pii_masker.py          # PII 마스킹
│   └── patterns.py            # PII 패턴 정의
└── audit/                      # 감사 로깅 모듈
    ├── __init__.py
    └── logger.py              # 감사 로깅
```

### 설계 원칙

1. **단일 책임**: 각 모듈은 하나의 명확한 목적을 가짐
2. **독립성**: 모듈간 강결합 없이 독립적으로 사용 가능
3. **확장성**: 새로운 가드레일 기능을 쉽게 추가 가능
4. **테스트 용이성**: 개별 모듈별 독립적 테스트
5. **명확성**: 혼선 없는 깔끔한 API 구조

## 🔧 사용법

### 1. Auth 모듈 - 권한 확인

```python
from py_common.guardrails.auth import require_permission, check_permission

# FastAPI 의존성으로 사용 (권장)
@app.post("/api/v1/journals")
async def create_journal(
    data: JournalCreate,
    _auth: None = require_permission("ledger:journals", "create")
):
    return await journal_service.create(data)

# 직접 호출로 사용
result = await check_permission(
    user_id="user123",
    resource="ledger:journals",
    action="create",
    tenant_id="tenant456"
)

if not result:
    raise HTTPException(status_code=403, detail="Permission denied")
```

### 2. Privacy 모듈 - PII 마스킹

```python
from py_common.guardrails.privacy import mask_pii_quick, PIIMasker
from py_common.guardrails.core import GuardrailConfig, PIIDetectionLevel

# 빠른 마스킹
def process_user_input(text: str) -> str:
    return mask_pii_quick(text, level=PIIDetectionLevel.ADVANCED)

# 세밀한 제어
config = GuardrailConfig(pii_detection_level=PIIDetectionLevel.ADVANCED)
masker = PIIMasker(config)
masked_text = await masker.mask_pii("사용자 홍길동의 주민번호는 123456-1234567입니다")
# 결과: "사용자 홍길동의 주민번호는 [SSN_KR]입니다"
```

### 3. Rate Limiting 모듈 - 사용량 제한

```python
from py_common.guardrails.rate_limiting import RateLimiter
from py_common.guardrails.core import GuardrailConfig

config = GuardrailConfig(
    enable_rate_limiting=True,
    rate_limit_requests_per_minute=60
)

limiter = RateLimiter(config)
allowed = await limiter.check_rate_limit("user123", "tenant456", "api")

if not allowed:
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### 4. Audit 모듈 - 감사 로깅

```python
from py_common.guardrails.audit import log_access_quick, AuditLogger
from py_common.guardrails.core import GuardrailConfig

# 빠른 감사 로깅
await log_access_quick(
    user_id="user123",
    resource="ledger:journals",
    action="create",
    allowed=True
)

# 세밀한 제어
config = GuardrailConfig(enable_audit_logging=True)
auditor = AuditLogger(config)
await auditor.log_access("user123", "tenant456", "journals", "create", True)
```

### 5. 복합 사용 - 여러 모듈 조합

```python
from py_common.guardrails import (
    require_permission,
    mask_pii_quick,
    log_access_quick
)

@app.post("/api/v1/sensitive-data")
async def process_sensitive_data(
    request: Request,
    data: SensitiveDataRequest,
    _auth: None = require_permission("data:sensitive", "process")
):
    # 1. PII 마스킹
    masked_input = mask_pii_quick(data.content)

    # 2. 비즈니스 로직 처리
    result = await sensitive_service.process(masked_input)

    # 3. 감사 로깅
    auth_context = get_auth_context(request)
    await log_access_quick(
        user_id=auth_context.user_id,
        resource="data:sensitive",
        action="process",
        allowed=True
    )

    return result
```

## 📝 서비스별 적용 예시

### 1. Ledger Service - 분개 처리

```python
# services/ledger/app/api/routes/journals.py
from py_common.guardrails import (
    require_permission,
    get_tenant_id,
    log_access_quick
)

@router.post("/")
async def create_journal(
    request: Request,
    data: JournalCreate,
    tenant_id: str = Depends(get_tenant_id),
    _auth: None = require_permission("ledger:journals", "create")
):
    """분개 생성 - 권한 확인 및 감사 로깅"""

    # 분개 생성
    journal = await journal_service.create(data, tenant_id)

    # 감사 로깅
    auth_context = get_auth_context(request)
    await log_access_quick(
        user_id=auth_context.user_id,
        resource="ledger:journals",
        action="create",
        allowed=True,
        details={"journal_id": journal.id}
    )

    return journal
```

### 2. Storage Service - 파일 업로드

```python
# services/storage/app/api/routes/files.py
from py_common.guardrails import (
    require_permission,
    get_tenant_id
)
from py_common.guardrails.rate_limiting import RateLimiter

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile,
    tenant_id: str = Depends(get_tenant_id),
    _auth: None = require_permission("storage:files", "upload")
):
    """파일 업로드 - 권한 확인 및 Rate Limiting"""

    # Rate Limiting 확인
    auth_context = get_auth_context(request)
    limiter = RateLimiter()
    allowed = await limiter.check_rate_limit(
        auth_context.user_id,
        tenant_id,
        "file-upload"
    )

    if not allowed:
        raise HTTPException(status_code=429, detail="Upload rate limit exceeded")

    # 파일 업로드
    result = await storage_service.upload(file, tenant_id)
    return result
```

### 3. AI Gateway - AI 요청 처리

```python
# services/ai-gw/app/api/routes/chat.py
from py_common.guardrails import (
    require_permission,
    mask_pii_quick
)
from py_common.guardrails.rate_limiting import RateLimiter

@router.post("/chat")
async def ai_chat(
    request: Request,
    data: ChatRequest,
    tenant_id: str = Depends(get_tenant_id),
    _auth: None = require_permission("ai:chat", "use")
):
    """AI 채팅 - PII 보호 및 사용량 제한"""

    # Rate Limiting (AI 사용량 제한)
    auth_context = get_auth_context(request)
    limiter = RateLimiter()
    allowed = await limiter.check_rate_limit(
        auth_context.user_id,
        tenant_id,
        "ai-chat"
    )

    if not allowed:
        raise HTTPException(status_code=429, detail="AI usage limit exceeded")

    # PII 마스킹
    safe_message = mask_pii_quick(data.message)

    # AI 처리
    response = await ai_service.chat(safe_message, tenant_id)
    return response
```

## 🔄 기존 서비스 마이그레이션 가이드

### Before (레거시 가드레일)

```python
from py_common.guardrails import authorize, get_tenant_id

@router.post("/")
async def create_resource(
    data: ResourceCreate,
    tenant_id: str = Depends(get_tenant_id),
    _auth: None = Depends(authorize)
):
    return await service.create(data, tenant_id)
```

### After (모듈형 가드레일)

```python
from py_common.guardrails import require_permission, get_tenant_id

@router.post("/")
async def create_resource(
    data: ResourceCreate,
    tenant_id: str = Depends(get_tenant_id),
    _auth: None = require_permission("service:resource", "create")
):
    return await service.create(data, tenant_id)
```

## 🚀 성능 최적화 설정

### 1. 캐시 최적화

```python
from py_common.guardrails.core import GuardrailConfig
from py_common.clients.unified_auth_client import AuthorizationStrategy

config = GuardrailConfig(
    # 권한 확인 캐시 (5분)
    auth_strategy=AuthorizationStrategy.RBAC_FALLBACK,
    enable_cache=True,
    cache_ttl=300,

    # Rate limiting 설정
    enable_rate_limiting=True,
    default_rate_limit=1000,  # 시간당 1000회

    # PII 감지 레벨
    pii_detection_level=PIIDetectionLevel.ADVANCED,

    # 감사 로깅
    enable_audit_logging=True,
    audit_sensitive_operations=True
)
```

### 2. 테넌트별 설정

```python
config = GuardrailConfig(
    tenant_rate_limit={
        "enterprise_tenant": 5000,  # 엔터프라이즈: 높은 제한
        "premium_tenant": 2000,     # 프리미엄: 중간 제한
        "basic_tenant": 500,        # 기본: 낮은 제한
    }
)
```

## 🧪 테스트 가이드

### 1. 단위 테스트

```python
import pytest
from py_common.guardrails.auth import check_permission
from py_common.guardrails.privacy import mask_pii_quick

@pytest.mark.asyncio
async def test_permission_check():
    """권한 확인 테스트"""
    allowed = await check_permission(
        user_id="test_user",
        resource="test:resource",
        action="read",
        tenant_id="test_tenant"
    )
    assert isinstance(allowed, bool)

def test_pii_masking():
    """PII 마스킹 테스트"""
    text = "홍길동의 이메일은 hong@example.com 입니다"
    masked = mask_pii_quick(text)
    assert "[EMAIL]" in masked
    assert "hong@example.com" not in masked
```

### 2. 통합 테스트

```python
from fastapi.testclient import TestClient

def test_guardrail_integration():
    """가드레일 통합 테스트"""
    response = client.post(
        "/api/v1/protected",
        headers={
            "Authorization": "Bearer valid_token",
            "X-Tenant-Id": "test_tenant"
        },
        json={"data": "test"}
    )
    assert response.status_code == 200
```

## 📋 마이그레이션 체크리스트

### 기존 서비스 전환

- [ ] **IAM Service**: 기존 가드레일 → 모듈형 가드레일
- [ ] **Tenant Service**: 기존 가드레일 → 모듈형 가드레일
- [ ] **Ledger Service**: 기존 가드레일 → 모듈형 가드레일
- [ ] **i18n Service**: 기존 가드레일 → 모듈형 가드레일

### 신규 서비스 적용

- [ ] **Template Service**: 모듈형 가드레일 적용
- [ ] **Storage Service**: 모듈형 가드레일 적용
- [ ] **AI Services**: 모듈형 가드레일 적용

### 검증 사항

- [ ] 모든 import 정상 작동 확인
- [ ] 기존 API 호환성 확인
- [ ] 성능 테스트 실행
- [ ] 보안 테스트 실행

---

## 🔗 관련 문서

- [py_common 체크리스트](../py_common_check_list.md): 개선 진행 상황
- [AUTH_RBAC_PROCESS.md](../../../AUTH_RBAC_PROCESS.md): 전체 인증/권한 아키텍처
- [IAM Service README](../../../services/iam/README.md): IAM 서비스 연동
- [RBAC Service README](../../../services/rbac/README.md): RBAC 서비스 연동

이 가이드는 MySingle 플랫폼의 모듈형 가드레일 시스템 사용법을 제공합니다. 각 모듈을 독립적으로 사용하거나 필요에 따라 조합하여 보안, 권한 관리, 감사 로깅을 구현하세요.
