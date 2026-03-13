"""Модуль фикстур для класса BaseProvider."""

from typing import AsyncGenerator

import pytest
from yarl import URL

from weblite_framework.provider.base_provider import BaseProvider


@pytest.fixture(scope='function')
async def provider() -> AsyncGenerator[BaseProvider, None]:
    """Создаёт экземпляр BaseProvider для тестов.

    Yields:
        BaseProvider: экземпляр провайдера с закрытием сессии после теста
    """
    provider = BaseProvider(base_url=URL('http://test'), timeout=10.0)
    try:
        yield provider
    finally:
        await provider.close()
