"""Модуль исключений, связанных с ошибками соединения."""

from weblite_framework.exceptions.base import BaseAppException

__all__ = [
    'ServiceHealthError',
    'DatabaseConnectionError',
    'AccessDeniedError',
]


class ServiceHealthError(Exception):
    """Базовое исключение для ошибок соединения с зависимостями."""

    def __init__(
        self,
        service_name: str,
        detail: str = 'Соединение отсутствует',
    ) -> None:
        """Инициализирует исключение, возникшее в слое репозитория.

        Args:
            service_name: Имя сервиса
            detail: Детали для уточнения ошибки
        """
        super().__init__(f'{service_name}: {detail}')


class DatabaseConnectionError(ServiceHealthError):
    """Исключение, возникающее при ошибке соединения с базой данных."""

    def __init__(
        self,
        detail: str = 'Ошибка подключения к БД',
    ) -> None:
        """Инициализирует исключение, возникшее с БД.

        Args:
            detail: Детали для уточнения ошибки
        """
        super().__init__(
            service_name='База данных',
            detail=detail,
        )


class AccessDeniedError(BaseAppException):
    """Исключение при отказе в доступе."""

    def __init__(self) -> None:
        """Инициализирует исключение AccessDeniedError."""
        super().__init__(
            status_code=403,
            detail='Доступ запрещен',
        )
