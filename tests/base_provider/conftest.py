"""Модуль фикстур для класса BaseProvider."""

from typing import AsyncGenerator

import pytest
from yarl import URL

from weblite_framework.provider.base_provider import BaseProvider


@pytest.fixture
def base_url() -> URL:
    """Фикстура базового URL.

    Returns:
        URL: Базовый URL для тестового сервиса.
    """
    return URL('http://test')


@pytest.fixture
def timeout() -> float:
    """Фикстура таймаута запроса.

    Returns:
        float: время таймаута типа float.
    """
    return 10.0


@pytest.fixture
async def provider(
    base_url: URL, timeout: float
) -> AsyncGenerator[BaseProvider]:
    """Создаёт экземпляр BaseProvider для тестов.

    Args:
        base_url: базовый URL сервиса
        timeout: timeout HTTP-запроса

    Yields:
        BaseProvider: экземпляр провайдера с закрытием сессии после теста.
    """
    provider = BaseProvider(base_url=base_url, timeout=timeout)
    try:
        yield provider
    finally:
        await provider.close()


@pytest.fixture
def path() -> str:
    """Возвращает путь тестового эндпоинта."""
    return '/v1/users/1'
