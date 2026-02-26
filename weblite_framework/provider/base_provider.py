"""Модуль для получения персональных данных с помощью базового провайдера."""

from typing import Any

import aiohttp

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
    ) -> dict[str, Any]:
        """Выполняет get - запрос.

        Args:
            url: адрес эндпоинта
            params: параметры запроса
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()  # type: ignore[no-any-return]

    async def post_data(
        self,
        url: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Выполняет post - запрос.

        Args:
            url: адрес эндпоинта
            data: тело запроса
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        async with self._session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()  # type: ignore[no-any-return]

    async def delete_data(
        self,
        url: str,
    ) -> dict[str, Any]:
        """Выполняет delete - запрос.

        Args:
            url: адрес эндпоинта
        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        async with self._session.delete(url) as response:
            response.raise_for_status()
            return await response.json()  # type: ignore[no-any-return]
