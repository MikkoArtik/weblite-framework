"""Модуль базового сервиса для работы с бизнес-логикой."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from weblite_framework.exceptions.service import AccessDeniedError

__all__ = ['BaseServiceClass']


DTO = TypeVar('DTO')
SCHEMA = TypeVar('SCHEMA')


class BaseServiceClass(Generic[DTO, SCHEMA], ABC):
    """Базовый сервис с общими методами."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует базовый сервис.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    @abstractmethod
    def _dto_to_schema(self, dto: DTO) -> SCHEMA:
        """Конвертирует DTO в Schema.

        Args:
            dto: Объект DTO

        Returns:
            SCHEMA: Объект схемы
        """
        pass

    @abstractmethod
    def _schema_to_dto(self, schema: SCHEMA) -> DTO:
        """Конвертирует Schema в DTO.

        Args:
            schema: Объект схемы

        Returns:
            DTO: Объект DTO
        """
        pass

    def _bulk_dto_to_schema(self, dtos: list[DTO]) -> list[SCHEMA]:
        """Конвертирует список DTO в список схем.

        Args:
            dtos: Список объектов DTO

        Returns:
            list[SCHEMA]: Список объектов схемы
        """
        schemas: list[SCHEMA] = []
        for dto in dtos:
            schema = self._dto_to_schema(dto)
            schemas.append(schema)
        return schemas

    def _bulk_schema_to_dto(self, schemas: list[SCHEMA]) -> list[DTO]:
        """Конвертирует список Schema в список DTO.

        Args:
            schemas: Список объектов схемы

        Returns:
            list[DTO]: Список объектов DTO
        """
        dtos: list[DTO] = []
        for schema in schemas:
            dto = self._schema_to_dto(schema)
            dtos.append(dto)
        return dtos

    async def _is_user_has_access(
        self,
        repository: Any,  # noqa: ANN401
        resume_id: int,
        user_id: int,
    ) -> None:
        """Метод проверяет доступ пользователя к резюме.

        Args:
            repository: Репозиторий с методом get_by_id
            resume_id: Идентификатор резюме
            user_id: Идентификатор пользователя

        Raises:
            AccessDeniedError: Если доступ запрещен
        """
        resume = await repository.get_by_id(id_=resume_id)
        if resume is None:
            raise AccessDeniedError()
        if not hasattr(resume, 'user_id'):
            raise AccessDeniedError()
        if resume.user_id != user_id:
            raise AccessDeniedError()
