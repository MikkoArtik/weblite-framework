"""Модуль для тестов класса базового провайдера BaseProvider."""

import pytest
import asyncio
import aiohttp

from unittest.mock import AsyncMock, MagicMock

from weblite_framework.provider.base_provider import BaseProvider


pytestmark = pytest.mark.asyncio


def make_mock_response(
    json_data: dict | None = None,
    raise_error: Exception | None = None,
):
    """Mock-объект response для aiohttp-запросов.

    Args:
        json_data: Возвращённые данные при вызове await response.json()
        raise_error: Исключение при неуспешном запросе

    Returns:
        AsyncMock: Mock - объект для дальнейших тестов
    """
    mock_response = AsyncMock()
    if raise_error:
        mock_response.raise_for_status.side_effect = raise_error
    else:
        mock_response.raise_for_status.return_value = None
    mock_response.json = AsyncMock(return_value=json_data)
    return mock_response


async def test_get_data_success():
    """Тест успешного выполнения get - запроса."""
    expected = {"status": "ok"}
    mock_session = MagicMock()
    mock_response = make_mock_response(json_data=expected)
    mock_session.get.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.get_data("/test")

    assert result == expected
    mock_session.get.assert_called_once_with("/test", params=None)


async def test_get_data_error():
    """Тест проверки обработки ошибки при выполнении get - запроса."""
    mock_session = MagicMock()

    mock_response = make_mock_response(
        raise_error=aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=500,
            message="error",
        )
    )

    mock_session.get.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.get_data("/test")

    assert result is None


async def test_post_data_success():
    """Тест успешного выполнения post - запроса."""
    expected = {"created": True}
    mock_session = MagicMock()
    mock_response = make_mock_response(json_data=expected)
    mock_session.post.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.post_data("/create", params={"name": "Alex"})

    assert result == expected
    mock_session.post.assert_called_once_with(
        "/create",
        json={"name": "Alex"},
    )


async def test_post_data_timeout():
    """Тест обработки таймаута при выполнении post - запроса."""
    mock_session = MagicMock()

    mock_response = make_mock_response(
        raise_error=asyncio.TimeoutError()
    )

    mock_session.post.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.post_data("/create")

    assert result is None


async def test_delete_data_success():
    """Тест успешного выполнения delete - запроса."""
    expected = {"deleted": True}

    mock_session = MagicMock()
    mock_response = make_mock_response(json_data=expected)
    mock_session.delete.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.delete_data("/delete")

    assert result == expected


async def test_delete_data_client_error():
    """Тест обработки клиентской ошибки при выполнении post - запроса."""
    mock_session = MagicMock()

    mock_response = make_mock_response(
        raise_error=aiohttp.ClientError()
    )

    mock_session.delete.return_value.__aenter__.return_value = mock_response
    provider = BaseProvider(session=mock_session)

    result = await provider.delete_data("/delete")

    assert result is None
