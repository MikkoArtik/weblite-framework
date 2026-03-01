"""Модуль перечислений (enums) для приложения."""

from enum import Enum

__all__ = [
    'HttpMethodEnum',
]


class HttpMethodEnum(str, Enum):
    """Класс HTTP-методов для выполнения запросов.

    Определяет и передаёт итп запроса в BaseProvider.

    Args:
        GET: GET-запрос
        POST: POST-запрос
        DELETE: DELETE-запрос
    """

    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
