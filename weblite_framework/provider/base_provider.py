"""Модуль для получения персональных данных с помощью базового провайдера."""

from enum import Enum
from typing import Any

import aiohttp
from yarl import URL

__all__ = [
    'BaseProvider',
]


class HttpMethod(str, Enum):
    """Класс HTTP-методов для выполнения запросов."""

    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'


class BaseProvider:
    """Родительский класс HTTP-провайдера для подключения к сервису."""

    def __init__(self, base_url: URL, timeout: float) -> None:
        """Инициализирует экземпляр класса BaseProvider.

        Args:
            base_url: url для подключения к сервису
            timeout: timeout запроса
        """
        self._base_url = base_url
        self._timeout = timeout

    async def request(
        self,
        method: HttpMethod,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Формирует общий вид запроса.

        Args:
            method: тип запроса
            path: адрес эндпоинта
            params: параметры запроса
            data: тело запроса

        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method,
                    url=self._base_url / path,
                    params=params,
                    data=data,
                ) as response:
                    response.raise_for_status()
                    return await response.json()  # type: ignore[no-any-return]
        except (
            aiohttp.ClientResponseError,
            aiohttp.ServerTimeoutError,
            aiohttp.ClientError,
        ):
            return None
