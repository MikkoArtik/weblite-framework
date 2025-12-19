"""Базовый сервис для всех сервисов приложения."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar, get_type_hints

from sqlalchemy.ext.asyncio import AsyncSession

from weblite_framework.exceptions.repository import RepositoryException

__all__ = ['BaseServiceClass']

RESUME_REPO_NOT_INITIALIZED_MSG = (
    'Репозиторий резюме не инициализирован. '
    'Для использования метода _is_user_has_access '
    'необходимо установить _resume_repo'
)

SCHEMA_NO_MODEL_DUMP_MSG = 'Схема должна иметь метод model_dump(): {}'

T_DTO = TypeVar('T_DTO')
T_SCHEMA = TypeVar('T_SCHEMA')


class BaseServiceClass(Generic[T_DTO, T_SCHEMA], ABC):
    """Базовый абстрактный сервис с утилитами для конвертации DTO ↔ Schema."""

    def __init__(
        self,
        session: AsyncSession,
        resume_repo: Optional[Any] = None,
    ) -> None:
        """Инициализирует базовый сервис.

        Args:
            session: SQLAlchemy async session
            resume_repo: Опциональный репозиторий для проверки доступа
        """
        self._session = session
        self._resume_repo = resume_repo

    @property
    @abstractmethod
    def DTO_CLASS(self) -> Type[T_DTO]:
        """Класс DTO, должен быть определен в дочернем классе."""
        pass

    @property
    @abstractmethod
    def SCHEMA_CLASS(self) -> Type[T_SCHEMA]:
        """Класс схемы, должен быть определен в дочернем классе."""
        pass

    def _get_schema_fields_from_type_hints(self) -> list[str]:
        """Получает поля схемы через get_type_hints.

        Returns:
            Список имен полей схемы
        """
        try:
            return list(get_type_hints(self.SCHEMA_CLASS).keys())
        except Exception as exc:
            error_msg = (
                f'Не удалось получить поля схемы {self.SCHEMA_CLASS.__name__} '
                f'через get_type_hints. Ошибка: {exc}'
            )
            raise RepositoryException(detail=error_msg) from exc

    def _get_schema_fields_from_annotations(self) -> list[str]:
        """Получает поля схемы через аннотации класса.

        Returns:
            Список имен полей схемы
        """
        if hasattr(self.SCHEMA_CLASS, '__annotations__'):
            return list(self.SCHEMA_CLASS.__annotations__.keys())
        return []

    def _get_schema_fields_from_instance(self) -> list[str]:  # noqa: C901
        """Получает поля схемы через создание экземпляра.

        Returns:
            Список имен полей схемы

        Raises:
            RepositoryException: Если не удалось создать экземпляр схемы
        """
        try:
            schema_instance = self.SCHEMA_CLASS()
        except Exception as exc:
            error_msg = (
                f'Не удалось создать экземпляр схемы '
                f'{self.SCHEMA_CLASS.__name__}. Ошибка: {exc}'
            )
            raise RepositoryException(detail=error_msg) from exc

        if not hasattr(schema_instance, '__dict__'):
            return []

        excluded_fields = {'model_fields', '__fields__'}
        result = []
        for field in schema_instance.__dict__.keys():
            if field.startswith('_'):
                continue
            if field in excluded_fields:
                continue
            result.append(field)
        return result

    def _get_schema_fields(self) -> list[str]:
        """Получает поля схемы используя различные методы.

        Returns:
            Список имен полей схемы
        """
        try:
            return self._get_schema_fields_from_type_hints()
        except RepositoryException:
            fields = self._get_schema_fields_from_annotations()
            if not fields:
                fields = self._get_schema_fields_from_instance()
            return fields

    def _dto_to_schema(
        self,
        dto: T_DTO,
    ) -> T_SCHEMA:
        """Конвертирует DTO в ResponseSchema.

        Args:
            dto: Объект DTO для конвертации

        Returns:
            Объект ResponseSchema

        Raises:
            RepositoryException: Если не удалось создать экземпляр схемы
        """
        data: dict[str, Any] = {}
        fields = self._get_schema_fields()

        for field_name in fields:
            if hasattr(
                dto,
                field_name,
            ):
                data[field_name] = getattr(
                    dto,
                    field_name,
                )

        try:
            return self.SCHEMA_CLASS(**data)
        except Exception as exc:
            error_msg = (
                f'Не удалось создать экземпляр схемы '
                f'{self.SCHEMA_CLASS.__name__}. Ошибка: {exc}'
            )
            raise RepositoryException(detail=error_msg) from exc

    def _schema_to_dto(
        self,
        schema: Any,  # noqa: ANN401
        **additional_fields: Any,  # noqa: ANN401
    ) -> T_DTO:
        """Конвертирует RequestSchema в DTO.

        Args:
            schema: RequestSchema объект с методом model_dump()
            **additional_fields: Дополнительные поля для DTO

        Returns:
            Объект DTO

        Raises:
            RepositoryException: Если схема не имеет метода model_dump()
        """
        try:
            data: dict[str, Any] = schema.model_dump()
        except AttributeError as exc:
            raise RepositoryException(
                detail=SCHEMA_NO_MODEL_DUMP_MSG.format(exc)
            ) from exc

        data.update(additional_fields)
        return self.DTO_CLASS(**data)

    def _bulk_dto_to_schema(
        self,
        dtos: list[T_DTO],
    ) -> list[T_SCHEMA]:
        """Конвертирует список DTO в список схем.

        Args:
            dtos: Список объектов DTO

        Returns:
            Список объектов ResponseSchema
        """
        schemas: list[T_SCHEMA] = []
        for dto in dtos:
            schema = self._dto_to_schema(dto)
            schemas.append(schema)
        return schemas

    def _bulk_schema_to_dto(
        self,
        schemas: list[Any],  # noqa: ANN401
        **additional_fields: Any,  # noqa: ANN401
    ) -> list[T_DTO]:
        """Конвертирует список RequestSchema в список DTO.

        Args:
            schemas: Список RequestSchema объектов
            **additional_fields: Дополнительные поля для всех DTO

        Returns:
            Список объектов DTO
        """
        dtos: list[T_DTO] = []
        for schema in schemas:
            dto = self._schema_to_dto(
                schema=schema,
                **additional_fields,
            )
            dtos.append(dto)
        return dtos

    async def _is_user_has_access(
        self,
        resume_id: int,
        user_id: int,
    ) -> bool:
        """Проверяет доступ пользователя к резюме.

        Args:
            resume_id: Идентификатор резюме
            user_id: Идентификатор пользователя

        Returns:
            True если резюме принадлежит пользователю,
            False в противном случае

        Raises:
            RepositoryException: Если _resume_repo не установлен
        """
        if self._resume_repo is None:
            raise RepositoryException(detail=RESUME_REPO_NOT_INITIALIZED_MSG)

        resume = await self._resume_repo.get_by_id(id_=resume_id)
        return resume is not None and resume.user_id == user_id
