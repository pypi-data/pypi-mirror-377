"""
CRUD Factory 모듈 - 재사용 가능한 CRUD 작업을 위한 팩토리 클래스

이 모듈은 다음 기능을 제공합니다:
1. 공통 CRUD 패턴 추상화
2. RBAC 권한 확인 자동화
3. 테넌트 격리 강제
4. 에러 처리 표준화
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from mysingle.base import BaseDoc, BaseResponseSchema
from mysingle.guardrails import get_tenant_id
from mysingle.logging import get_logger
from mysingle.rbac import audit_log, require_permission

logger = get_logger(__name__)


class BaseCRUDService:
    """기본 CRUD 서비스 클래스"""

    def __init__(
        self,
        model: Type[BaseDoc],
        resource_name: str,
        service_prefix: str = "ledger",
    ):
        self.model = model
        self.resource_name = resource_name
        self.service_prefix = service_prefix

    async def create(
        self,
        data: Dict[str, Any],
        tenant_id: str,
        user_id: Optional[str] = None,
    ) -> BaseDoc:
        """리소스 생성"""
        try:
            # 기본 메타데이터 추가
            data["tenant_id"] = tenant_id
            data["created_at"] = datetime.now(timezone.utc)
            data["updated_at"] = None
            data["idempotency_key"] = None

            # 모델 생성 및 저장
            instance = self.model(**data)
            await instance.insert()

            # 로깅
            logger.info(
                f"Created {self.resource_name}: {instance.id} for tenant: {tenant_id}"
            )

            return instance

        except Exception as e:
            logger.error(f"Failed to create {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create {self.resource_name}",
            )

    async def list(
        self,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[BaseDoc]:
        """리소스 목록 조회"""
        try:
            # 기본 쿼리 구성
            query = {"tenant_id": tenant_id}
            if filters:
                query.update(filters)

            # 데이터 조회
            items = (
                await self.model.find(query).skip(skip).limit(limit).to_list()
            )
            return items

        except Exception as e:
            logger.error(f"Failed to list {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list {self.resource_name}",
            )

    async def get(
        self,
        item_id: str,
        tenant_id: str,
    ) -> BaseDoc:
        """리소스 단건 조회"""
        try:
            item = await self.model.get(item_id)
            if not item or item.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            return item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get {self.resource_name}",
            )

    async def update(
        self,
        item_id: str,
        data: Dict[str, Any],
        tenant_id: str,
        user_id: Optional[str] = None,
    ) -> BaseDoc:
        """리소스 업데이트"""
        try:
            # 기존 항목 조회
            item = await self.model.get(item_id)
            if not item or item.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 업데이트 데이터 준비
            data["updated_at"] = datetime.now(timezone.utc)

            # 업데이트 실행
            await item.set(data)
            await item.save()

            # 로깅
            logger.info(
                f"Updated {self.resource_name}: {item_id} for tenant: {tenant_id}"
            )

            return item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update {self.resource_name}",
            )

    async def delete(
        self,
        item_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        """리소스 삭제"""
        try:
            # 기존 항목 조회
            item = await self.model.get(item_id)
            if not item or item.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 삭제 실행
            await item.delete()

            # 로깅
            logger.info(
                f"Deleted {self.resource_name}: {item_id} for tenant: {tenant_id}"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete {self.resource_name}",
            )


def create_crud_router(
    service: BaseCRUDService,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    response_schema: Type[BaseResponseSchema],
    prefix: str = "",
    include_operations: Optional[List[str]] = None,
) -> APIRouter:
    """
    CRUD 라우터 생성 함수

    Args:
        service: CRUD 서비스 인스턴스
        create_schema: 생성 스키마 클래스
        update_schema: 업데이트 스키마 클래스
        response_schema: 응답 스키마 클래스
        prefix: 라우터 URL 접두사
        include_operations: 포함할 작업 목록 (기본: 모든 작업)

    Returns:
        구성된 APIRouter 인스턴스
    """
    router = APIRouter(
        prefix=prefix,
        dependencies=[Depends(get_tenant_id)],
    )

    operations = include_operations or [
        "create",
        "list",
        "get",
        "update",
        "delete",
    ]

    # CREATE 엔드포인트
    if "create" in operations:

        @router.post(
            "",
            status_code=status.HTTP_201_CREATED,
            response_model=response_schema,
        )
        @audit_log("create", service.resource_name)
        async def create_item(
            data: create_schema,  # type: ignore
            tenant_id: str = Depends(get_tenant_id),
            _auth: Any = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "create",
                )
            ),
        ):
            result = await service.create(data.model_dump(), tenant_id)  # type: ignore
            return response_schema.model_validate(result, from_attributes=True)

    # LIST 엔드포인트
    if "list" in operations:

        @router.get(
            "",
            response_model=List[response_schema],  # type: ignore
        )
        @audit_log("list", service.resource_name)
        async def list_items(
            tenant_id: str = Depends(get_tenant_id),
            limit: int = 100,
            skip: int = 0,
            _auth: Any = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}", "read"
                )
            ),
        ):
            results = await service.list(tenant_id, limit=limit, skip=skip)
            return [
                response_schema.model_validate(item, from_attributes=True)
                for item in results
            ]

    # GET 엔드포인트
    if "get" in operations:

        @router.get(
            "/{item_id}",
            response_model=response_schema,
        )
        @audit_log("get", service.resource_name)
        async def get_item(
            item_id: str,
            tenant_id: str = Depends(get_tenant_id),
            _auth: Any = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}", "read"
                )
            ),
        ):
            result = await service.get(item_id, tenant_id)
            return response_schema.model_validate(result, from_attributes=True)

    # UPDATE 엔드포인트
    if "update" in operations:

        @router.put(
            "/{item_id}",
            response_model=response_schema,
        )
        @audit_log("update", service.resource_name)
        async def update_item(
            item_id: str,
            data: update_schema,  # type: ignore
            tenant_id: str = Depends(get_tenant_id),
            _auth: Any = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "update",
                )
            ),
        ):
            result = await service.update(
                item_id,
                data.model_dump(exclude_unset=True),  # type: ignore
                tenant_id,
            )
            return response_schema.model_validate(result, from_attributes=True)

    # DELETE 엔드포인트
    if "delete" in operations:

        @router.delete(
            "/{item_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        @audit_log("delete", service.resource_name)
        async def delete_item(
            item_id: str,
            tenant_id: str = Depends(get_tenant_id),
            _auth: Any = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "delete",
                )
            ),
        ):
            await service.delete(item_id, tenant_id)

    return router
