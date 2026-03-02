"""Модуль для получения персональных данных с помощью базового провайдера."""

from http import HTTPMethod
from typing import Any

import aiohttp
from aiohttp import ClientSession, ClientTimeout
from yarl import URL

from weblite_framework.exceptions.auth import UnauthorizedException
from weblite_framework.exceptions.base import BaseAppException

__all__ = [
    'BaseProvider',
]


class BaseProvider(ClientSession):
    """Родительский класс HTTP-провайдера для подключения к сервису."""

    def __init__(self, base_url: URL, timeout: float) -> None:
        """Инициализирует экземпляр класса BaseProvider.

        Args:
            base_url: url для подключения к сервису
            timeout: timeout запроса
        """
        super().__init__(
            base_url=base_url,
            timeout=ClientTimeout(total=timeout),
        )

    async def _create_request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Формирует общий вид запроса.

        Args:
            method: тип запроса
            path: адрес эндпоинта
            params: параметры запроса
            data: тело запроса
            headers: необязательные заголовки запроса

        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        try:
            async with super().request(
                method=method,
                url=path,
                params=params,
                data=data,
                headers=headers,
            ) as response:
                payload = await response.json()
                await self.check_response_status(response=response)
                return payload if payload else {}
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError) as exc:
            raise BaseAppException(
                status_code=503,
                detail=f'Ошибка доступа к сервису: {exc}',
            )

    async def check_response_status(
        self,
        response: aiohttp.ClientResponse,
    ) -> None:
        """Проверяет статус ответа.

        Args:
            response: объект ответа от сервиса

        Raises:
            UnauthorizedException: если статус 401
            BaseAppException: если статус 5xx или другой HTTP статус
        """
        if response.status == 401:
            raise UnauthorizedException(
                detail=f'Сервис вернул HTTP {response.status} - авторизация не пройдена.',  # noqa: E501
            )

        if response.status >= 500:
            raise BaseAppException(
                status_code=503,
                detail=f'Сервис вернул {response.status} — временно недоступен.',  # noqa: E501
            )

        elif response.status != 200:
            raise BaseAppException(
                status_code=500,
                detail=f'Неожиданный ответ от сервиса: {response.status}',  # noqa: E501
            )
