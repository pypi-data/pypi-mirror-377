"""PII 마스킹 로직"""

import re
from typing import List, Optional

from mysingle.logging import get_logger

from ..core.base import IPIIMasker
from ..core.config import GuardrailConfig, PIIDetectionLevel
from .patterns import PIIPattern, PIIPatterns

logger = get_logger(__name__)


class PIIMasker(IPIIMasker):
    """PII 마스킹 구현"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self._patterns: List[PIIPattern] = []
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        """패턴 초기화"""
        self._patterns = PIIPatterns.get_patterns_by_level(
            self.config.pii_detection_level
        )
        logger.info(
            f"PII masker initialized with {len(self._patterns)} patterns "
            f"(level: {self.config.pii_detection_level})"
        )

    def mask_pii(self, text: str) -> str:
        """PII 마스킹"""
        if not self.config.enable_pii_masking:
            return text

        if self.config.pii_detection_level == PIIDetectionLevel.AI.value:
            return self._mask_pii_ai(text)
        else:
            return self._mask_pii_regex(text)

    def _mask_pii_regex(self, text: str) -> str:
        """정규식 기반 PII 마스킹"""
        masked_text = text

        for pattern in self._patterns:
            try:
                masked_text = re.sub(
                    pattern.pattern,
                    pattern.replacement,
                    masked_text,
                    flags=pattern.flags,
                )
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern.name}: {e}")
                continue

        return masked_text

    def _mask_pii_ai(self, text: str) -> str:
        """AI 기반 PII 마스킹 (향후 구현)"""
        # TODO: AI 기반 PII 감지 및 마스킹 구현
        # 현재는 고급 정규식 마스킹 사용
        logger.warning(
            "AI-based PII masking not implemented, using advanced regex"
        )
        return self._mask_pii_regex(text)

    def mask_specific_pii(self, text: str, pattern_names: List[str]) -> str:
        """특정 PII 패턴만 마스킹"""
        masked_text = text

        for pattern_name in pattern_names:
            try:
                pattern = PIIPatterns.get_pattern_by_name(pattern_name)
                masked_text = re.sub(
                    pattern.pattern,
                    pattern.replacement,
                    masked_text,
                    flags=pattern.flags,
                )
            except ValueError:
                logger.warning(f"Pattern not found: {pattern_name}")
                continue
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern_name}: {e}")
                continue

        return masked_text

    def detect_pii_types(self, text: str) -> List[str]:
        """텍스트에서 감지된 PII 타입 반환"""
        detected_types = []

        for pattern in self._patterns:
            try:
                if re.search(pattern.pattern, text, flags=pattern.flags):
                    detected_types.append(pattern.name)
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern.name}: {e}")
                continue

        return detected_types

    def get_supported_patterns(self) -> List[str]:
        """지원되는 패턴 이름 목록 반환"""
        return [pattern.name for pattern in self._patterns]

    def add_custom_pattern(self, pattern: PIIPattern) -> None:
        """커스텀 패턴 추가"""
        self._patterns.append(pattern)
        logger.info(f"Added custom PII pattern: {pattern.name}")

    def remove_pattern(self, pattern_name: str) -> bool:
        """패턴 제거"""
        for i, pattern in enumerate(self._patterns):
            if pattern.name == pattern_name:
                del self._patterns[i]
                logger.info(f"Removed PII pattern: {pattern_name}")
                return True
        return False


# 전역 PII 마스커
_pii_masker: Optional[PIIMasker] = None


def get_pii_masker(config: Optional[GuardrailConfig] = None) -> PIIMasker:
    """PII 마스커 싱글톤 인스턴스 반환"""
    global _pii_masker
    if _pii_masker is None:
        _pii_masker = PIIMasker(config or GuardrailConfig())
    return _pii_masker


def mask_pii_quick(text: str, level: str = "advanced") -> str:
    """빠른 PII 마스킹 (동기 함수)"""
    config = GuardrailConfig(pii_detection_level=level)
    masker = PIIMasker(config)
    return masker.mask_pii(text)
