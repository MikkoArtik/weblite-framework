import asyncio

import aiohttp
from typing import Any

__all__ = [
    'BaseProvider',
]


class BaseProvider:
    """Родительский класс HTTP-провайдера для подключения к сервису."""

    def __init__(
            self,
            session: aiohttp.ClientSession,
    ) -> None:
        """Инициализирует экземпляр класса BaseProvider.

        Args:
            session: HTTP-сессия
        """
        self._session = session


    async def get_data(
            self,
            url: str,
            params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Выполняет get - запрос.

        Args:
            url: адрес эндпоинта
            params: параметры запроса
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
            None: при ошибке запроса
        """
        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except (
            aiohttp.ClientResponseError,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ):
            return None


    async def post_data(
            self,
            url: str,
            params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Выполняет post - запрос.

        Args:
            url: адрес эндпоинта
            params: параметры запроса
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
            None: при ошибке запроса
        """
        try:
            async with self._session.post(url, json=params) as response:
                response.raise_for_status()
                return await response.json()
        except (
            aiohttp.ClientResponseError,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ):
            return None


    async def delete_data(
            self,
            url: str,
            params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Выполняет delete - запрос.

        Args:
            url: адрес эндпоинта
            params: параметры запроса
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
            None: при ошибке запроса
        """
        try:
            async with self._session.delete(url, json=params) as response:
                response.raise_for_status()
                return await response.json()
        except (
            aiohttp.ClientResponseError,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ):
            return None
