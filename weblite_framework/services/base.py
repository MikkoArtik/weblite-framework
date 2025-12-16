"""Базовый сервис для всех сервисов приложения."""

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    get_type_hints,
)

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


class BaseServiceClass(Generic[T_DTO, T_SCHEMA]):
    """Базовый сервис с приватными утилитами для конвертации DTO ↔ Schema.

    Примечание:
    - Все методы с префиксом '_' предназначены для ВНУТРЕННЕГО использования
      в дочерних сервисах проекта
    - В проектах должны оставаться свои приватные методы с '__'
    """

    DTO_CLASS: Type[T_DTO]
    SCHEMA_CLASS: Type[T_SCHEMA]

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """Инициализирует базовый сервис.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session
        self._resume_repo: Optional[Any] = None

    async def _is_user_has_access(
        self,
        resume_id: int,
        user_id: int,
    ) -> bool:
        """Проверяет доступ пользователя к резюме.

        Данный метод проверяет, что резюме
        принадлежит текущему пользователю.

        Args:
            resume_id: Идентификатор резюме
            user_id: Идентификатор пользователя

        Returns:
            bool: True если резюме принадлежит пользователю,
                False в противном случае

        Raises:
            RepositoryException: Если _resume_repo не установлен
        """
        if self._resume_repo is None:
            raise RepositoryException(detail=RESUME_REPO_NOT_INITIALIZED_MSG)

        resume = await self._resume_repo.get_by_id(id_=resume_id)
        return resume is not None and resume.user_id == user_id

    def _dto_to_schema(
        self,
        dto: T_DTO,
    ) -> T_SCHEMA:
        """Конвертирует DTO в ResponseSchema.

        Автоматически исключает поля, которых нет в схеме.

        Args:
            dto: Объект DTO для конвертации

        Returns:
            Объект ResponseSchema
        """
        data: Dict[str, Any] = {}

        fields = self._get_schema_fields_from_instance()
        if not fields:
            fields = self._get_schema_fields_from_annotations()
        if not fields:
            fields = self._get_schema_fields_from_type_hints()

        for field_name in fields:
            if hasattr(dto, field_name):
                data[field_name] = getattr(dto, field_name)

        return self.SCHEMA_CLASS(**data)

    def _get_schema_fields_from_instance(self) -> List[str]:
        """Получает поля схемы через создание экземпляра.

        Returns:
            Список имен полей схемы
        """
        try:
            schema_instance = self.SCHEMA_CLASS()
            if hasattr(schema_instance, '__dict__'):
                return list(schema_instance.__dict__.keys())
        except Exception:
            pass
        return []

    def _get_schema_fields_from_annotations(self) -> List[str]:
        """Получает поля схемы через аннотации класса.

        Returns:
            Список имен полей схемы
        """
        if hasattr(self.SCHEMA_CLASS, '__annotations__'):
            return list(self.SCHEMA_CLASS.__annotations__.keys())
        return []

    def _get_schema_fields_from_type_hints(self) -> List[str]:
        """Получает поля схемы через get_type_hints.

        Returns:
            Список имен полей схемы
        """
        try:
            return list(get_type_hints(self.SCHEMA_CLASS).keys())
        except Exception:
            return []

    def _bulk_dto_to_schema(
        self,
        dtos: List[T_DTO],
    ) -> List[T_SCHEMA]:
        """Конвертирует список DTO в список схем.

        Args:
            dtos: Список объектов DTO

        Returns:
            Список объектов ResponseSchema
        """
        return [self._dto_to_schema(dto) for dto in dtos]

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
            data: Dict[str, Any] = schema.model_dump()
        except AttributeError as exc:
            raise RepositoryException(
                detail=SCHEMA_NO_MODEL_DUMP_MSG.format(exc)
            ) from exc

        data.update(additional_fields)
        return self.DTO_CLASS(**data)

    def _bulk_schema_to_dto(
        self,
        schemas: List[Any],  # noqa: ANN401
        **additional_fields: Any,  # noqa: ANN401
    ) -> List[T_DTO]:
        """Конвертирует список RequestSchema в список DTO.

        Args:
            schemas: Список RequestSchema объектов
            **additional_fields: Дополнительные поля для всех DTO

        Returns:
            Список объектов DTO
        """
        dtos: List[T_DTO] = []
        for schema in schemas:
            dto = self._schema_to_dto(
                schema=schema,
                **additional_fields,
            )
            dtos.append(dto)
        return dtos
