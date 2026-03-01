"""Модуль для получения персональных данных с помощью базового провайдера."""

from typing import Any

import aiohttp
from yarl import URL

from weblite_framework.enums import HttpMethodEnum

__all__ = [
    'BaseProvider',
]

from weblite_framework.exceptions.auth import UnauthorizedException
from weblite_framework.exceptions.base import BaseAppException


class BaseProvider:
    """Родительский класс HTTP-провайдера для подключения к сервису."""

    def __init__(self, base_url: URL, timeout: float) -> None:
        """Инициализирует экземпляр класса BaseProvider.

        Args:
            base_url: url для подключения к сервису
            timeout: timeout запроса
        """
        self.__base_url = base_url
        self.__timeout = timeout

    async def request(
        self,
        method: HttpMethodEnum,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Формирует общий вид запроса.

        Args:
            method: тип запроса
            path: адрес эндпоинта
            params: параметры запроса
            data: тело запроса
            headers: валидационные параметры запроса

        Returns:
            dict[str, Any]: ответ сервиса при успешном запросе
        """
        timeout = aiohttp.ClientTimeout(total=self.__timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method,
                    url=self.__base_url / path,
                    params=params,
                    data=data,
                    headers=headers,
                ) as response:
                    payload = await response.json()
                    await self.check_response_status(
                        response=response,
                    )
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
            payload = await response.json()
            message = payload.get('message')
            raise UnauthorizedException(detail=message)

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
