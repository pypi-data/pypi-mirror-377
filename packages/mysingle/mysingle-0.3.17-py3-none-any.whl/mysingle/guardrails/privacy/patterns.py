"""PII 감지 패턴 정의"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class PIIPattern:
    """PII 패턴 정의"""

    name: str
    pattern: str
    replacement: str
    description: str
    flags: int = re.IGNORECASE


class PIIPatterns:
    """PII 패턴 모음"""

    # 기본 패턴들
    BASIC_PATTERNS = [
        PIIPattern(
            name="email",
            pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            replacement="[EMAIL]",
            description="이메일 주소",
        ),
        PIIPattern(
            name="phone",
            pattern=r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b",
            replacement="[PHONE]",
            description="전화번호",
        ),
        PIIPattern(
            name="credit_card",
            pattern=r"\b(?:\d[ -]*?){13,16}\b",
            replacement="[CARD]",
            description="신용카드 번호",
        ),
    ]

    # 고급 패턴들 (한국 특화)
    ADVANCED_PATTERNS = [
        PIIPattern(
            name="ssn_kr",
            pattern=r"\b\d{6}-[1-4]\d{6}\b",
            replacement="[SSN_KR]",
            description="주민등록번호 (한국)",
        ),
        PIIPattern(
            name="passport",
            pattern=r"\b[A-Z]{1,2}\d{7,9}\b",
            replacement="[PASSPORT]",
            description="여권번호",
        ),
        PIIPattern(
            name="license_kr",
            pattern=r"\b\d{2}-\d{2}-\d{6}-\d{2}\b",
            replacement="[LICENSE_KR]",
            description="운전면허번호 (한국)",
        ),
        PIIPattern(
            name="ip_address",
            pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            replacement="[IP_ADDRESS]",
            description="IP 주소",
        ),
        PIIPattern(
            name="mac_address",
            pattern=r"\b[0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}\b",
            replacement="[MAC_ADDRESS]",
            description="MAC 주소",
        ),
        PIIPattern(
            name="business_number_kr",
            pattern=r"\b\d{3}-\d{2}-\d{5}\b",
            replacement="[BUSINESS_NUM_KR]",
            description="사업자등록번호 (한국)",
        ),
        PIIPattern(
            name="account_number",
            pattern=r"\b\d{10,14}\b",
            replacement="[ACCOUNT]",
            description="계좌번호",
        ),
    ]

    # AI 기반 패턴들 (향후 구현)
    AI_PATTERNS: List[PIIPattern] = [
        # TODO: AI 기반 PII 감지 패턴 추가
    ]

    @classmethod
    def get_patterns_by_level(cls, level: str) -> List[PIIPattern]:
        """레벨별 패턴 반환"""
        if level == "basic":
            return cls.BASIC_PATTERNS
        elif level == "advanced":
            return cls.BASIC_PATTERNS + cls.ADVANCED_PATTERNS
        elif level == "ai":
            return cls.BASIC_PATTERNS + cls.ADVANCED_PATTERNS + cls.AI_PATTERNS
        else:
            return cls.BASIC_PATTERNS

    @classmethod
    def get_pattern_by_name(cls, name: str) -> PIIPattern:
        """이름으로 패턴 조회"""
        all_patterns = (
            cls.BASIC_PATTERNS + cls.ADVANCED_PATTERNS + cls.AI_PATTERNS
        )
        for pattern in all_patterns:
            if pattern.name == name:
                return pattern
        raise ValueError(f"Pattern not found: {name}")

    @classmethod
    def add_custom_pattern(cls, pattern: PIIPattern) -> None:
        """커스텀 패턴 추가"""
        # 실제 구현에서는 동적 패턴 추가 지원
        pass
