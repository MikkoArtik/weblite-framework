"""Модуль исключений, связанных с ошибками в слое репозитория."""

from fastapi import HTTPException, status

__all__ = [
    'RepositoryException',
]


class RepositoryException(HTTPException):
    """Класс исключения, связанного с БД."""

    def __init__(
        self,
        detail: str = 'Ошибка при работе с репозиторием',
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """Инициализирует исключение, возникшее в слое репозитория.

        Args:
            detail: Сообщение с передаваемой информацией
            status_code: Передаваемый HTTP код для уточнения ошибки
        """
        super().__init__(
            status_code=status_code,
            detail=detail,
        )
