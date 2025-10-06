"""Модуль исключений, связанных с авторизацией и правами доступа."""

from fastapi import HTTPException, status

__all__ = [
    'UnauthorizedException',
    'ForbiddenException',
]


class UnauthorizedException(HTTPException):
    """Класс исключения, связанного с авторизацией."""

    def __init__(self, detail: str = 'Необходима авторизация') -> None:
        """Инициализирует исключение при отсутствии авторизации.

        Args:
            detail: Сообщение с передаваемой информацией
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ForbiddenException(HTTPException):
    """Класс исключения, вызываемого при отсутствии прав доступа к ресурсу."""

    def __init__(
        self,
        detail: str = 'Доступ запрещён. У вас нет прав на выполнение данного '
        'действия.',
    ) -> None:
        """Инициализирует исключение при отсутствии прав доступа.

        Args:
            detail: Сообщение с передаваемой информацией
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
