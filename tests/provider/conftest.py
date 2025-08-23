"""Модуль фикстур для S2Provider."""

from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from weblite_framework.provider.s3 import S3Provider
from weblite_framework.settings.s3 import S3Settings


@pytest.fixture
def s3_settings() -> S3Settings:
    """Возвращает тестовые настройки для S3 (без чтения .env).

    Returns:
        S3Settings: Объект настроек для тестового окружения.
    """
    return S3Settings.model_construct(
        bucket='test_bucket',
        access_key='ak',
        secret_key='sk',
        region='us-east-1',
        endpoint_url='http://dummy:9090',
        path_style=True,
        signature_version='s3v4',
        max_attempts=3,
        connect_timeout=5,
        read_timeout=30,
    )


@pytest.fixture
def mocked_s3() -> tuple[AsyncMock, MagicMock]:
    """Создаёт моки для s3_client и aioboto3.Session.

    Returns:
        tuple: Кортеж из мокнутого клиента S3 и мокнутой сессии.
    """
    s3_client: AsyncMock = AsyncMock()

    client_cm: AsyncMock = AsyncMock()
    client_cm.__aenter__.return_value = s3_client
    client_cm.__aexit__.return_value = False

    session_mock: MagicMock = MagicMock()
    session_mock.client.return_value = client_cm
    return s3_client, session_mock


@pytest.fixture
def s3_client(mocked_s3: tuple[AsyncMock, MagicMock]) -> AsyncMock:
    """Возвращает мокнутый S3 client.

    Args:
        mocked_s3: Пара из фикстуры mocked_s3.

    Returns:
        AsyncMock: Экземпляр мокнутого клиента S3.
    """
    client, _ = mocked_s3
    return client


@pytest.fixture
async def provider(
    s3_settings: S3Settings,
    mocked_s3: tuple[AsyncMock, MagicMock],
) -> AsyncIterator[S3Provider]:
    """Создаёт провайдер S3Provider внутри контекста.

    Патчит ``aioboto3.Session`` так, чтобы он возвращал мокнутую сессию.

    Args:
        s3_settings: Тестовые настройки S3.
        mocked_s3: Моки клиента и сессии.

    Yields:
        S3Provider: Экземпляр провайдера с открытым мокнутым клиентом.
    """
    _, session_mock = mocked_s3

    with patch('aioboto3.Session', return_value=session_mock):
        async with S3Provider(settings=s3_settings) as p:
            yield p
