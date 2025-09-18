"""감사 로깅 로직"""

import json
import time
from typing import Any, Dict, Optional

from mysingle.logging import get_logger

from ..core.base import IAuditLogger
from ..core.config import GuardrailConfig

logger = get_logger(__name__)


class AuditLogger(IAuditLogger):
    """감사 로거 구현"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self._audit_buffer: list[Dict[str, Any]] = []
        self._buffer_size = 100  # 배치 처리를 위한 버퍼 크기

    async def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool,
        tenant_id: Optional[str] = None,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """접근 로그 기록"""
        if not self.config.enable_audit_logging:
            return

        audit_data = {
            "timestamp": time.time(),
            "event_type": "access_control",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "resource": resource,
            "action": action,
            "allowed": allowed,
            "reason": reason,
            "context": context,
            "strategy": self.config.auth_strategy.value,
        }

        await self._write_audit_log(audit_data)

    async def log_rate_limit(
        self,
        user_id: str,
        tenant_id: Optional[str],
        endpoint: str,
        limit_exceeded: bool,
        current_count: int,
        limit: int,
    ) -> None:
        """Rate limit 로그 기록"""
        if not self.config.enable_audit_logging:
            return

        audit_data = {
            "timestamp": time.time(),
            "event_type": "rate_limit",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "endpoint": endpoint,
            "limit_exceeded": limit_exceeded,
            "current_count": current_count,
            "limit": limit,
        }

        await self._write_audit_log(audit_data)

    async def log_pii_detection(
        self,
        user_id: Optional[str],
        tenant_id: Optional[str],
        detected_types: list[str],
        text_length: int,
        masked_length: int,
    ) -> None:
        """PII 감지 로그 기록"""
        if not self.config.enable_audit_logging:
            return

        audit_data = {
            "timestamp": time.time(),
            "event_type": "pii_detection",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "detected_pii_types": detected_types,
            "original_length": text_length,
            "masked_length": masked_length,
            "pii_count": len(detected_types),
        }

        await self._write_audit_log(audit_data)

    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        tenant_id: Optional[str],
        severity: str,
        details: Dict[str, Any],
    ) -> None:
        """보안 이벤트 로그 기록"""
        if not self.config.enable_audit_logging:
            return

        audit_data = {
            "timestamp": time.time(),
            "event_type": f"security_{event_type}",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "severity": severity,
            "details": details,
        }

        await self._write_audit_log(audit_data)

    async def _write_audit_log(self, audit_data: Dict[str, Any]) -> None:
        """감사 로그 실제 기록"""
        # 민감한 정보는 마스킹
        sanitized_data = self._sanitize_audit_data(audit_data)

        # 현재는 logger로 출력, 실제 환경에서는 별도 감사 로그 시스템으로 전송
        logger.info(f"AUDIT: {json.dumps(sanitized_data, ensure_ascii=False)}")

        # 버퍼에 추가 (배치 처리용)
        self._audit_buffer.append(sanitized_data)

        # 버퍼가 가득 차면 배치 처리
        if len(self._audit_buffer) >= self._buffer_size:
            await self._flush_audit_buffer()

    def _sanitize_audit_data(
        self, audit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감사 로그 데이터 새니타이제이션"""
        sanitized = audit_data.copy()

        # 민감한 필드들을 마스킹
        sensitive_fields = ["password", "token", "secret", "key"]

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"

        # 컨텍스트 내 민감한 정보 마스킹
        if "context" in sanitized and isinstance(sanitized["context"], dict):
            for field in sensitive_fields:
                if field in sanitized["context"]:
                    sanitized["context"][field] = "[REDACTED]"

        return sanitized

    async def _flush_audit_buffer(self) -> None:
        """감사 로그 버퍼 플러시"""
        if not self._audit_buffer:
            return

        # 실제 환경에서는 외부 시스템으로 배치 전송
        logger.debug(f"Flushing {len(self._audit_buffer)} audit logs")

        # TODO: 실제 감사 로그 시스템으로 전송
        # await self._send_to_audit_system(self._audit_buffer)

        self._audit_buffer.clear()

    async def get_audit_stats(self) -> Dict[str, Any]:
        """감사 로그 통계 반환"""
        return {
            "buffer_size": len(self._audit_buffer),
            "buffer_limit": self._buffer_size,
            "audit_enabled": self.config.enable_audit_logging,
            "sensitive_operations_audit": self.config.audit_sensitive_operations,
        }

    async def cleanup(self) -> None:
        """감사 로거 정리"""
        await self._flush_audit_buffer()


# 전역 감사 로거
_audit_logger: Optional[AuditLogger] = None


async def get_audit_logger(
    config: Optional[GuardrailConfig] = None,
) -> AuditLogger:
    """감사 로거 싱글톤 인스턴스 반환"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(config or GuardrailConfig())
    return _audit_logger


async def log_access_quick(
    user_id: str,
    resource: str,
    action: str,
    allowed: bool,
    tenant_id: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    """빠른 접근 로그 기록"""
    audit_logger = await get_audit_logger()
    await audit_logger.log_access(
        user_id=user_id,
        resource=resource,
        action=action,
        allowed=allowed,
        tenant_id=tenant_id,
        reason=reason,
    )
