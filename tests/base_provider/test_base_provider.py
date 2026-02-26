"""Модуль для тестов класса базового провайдера BaseProvider."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from hamcrest import assert_that, equal_to

from weblite_framework.provider.base_provider import BaseProvider

pytestmark = pytest.mark.asyncio


class TestBaseProvider:
    """Тесты для класса BaseProvider."""

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='get',
    )
    async def test_get_data_success(
        self,
        mock_get: AsyncMock,
    ) -> None:
        """Тест успешного выполнения get - запроса.

        Args:
            mock_get: Мок метода aiohttp.ClientSession.get
        """
        expected = {'status': 'ok'}
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json = AsyncMock(return_value=expected)

        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)
            result = await provider.get_data('/test')

        assert_that(actual_or_assertion=result, matcher=equal_to(expected))
        mock_get.assert_called_once_with('/test', params=None)
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_awaited_once()

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='get',
    )
    async def test_get_data_error(self, mock_get: AsyncMock) -> None:
        """Тест проверки обработки ошибки при выполнении get - запроса.

        Args:
            mock_get: Мок метода aiohttp.ClientSession.get
        """
        err = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=500,
            message='error',
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = err
        mock_response.json = AsyncMock()

        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)

            with pytest.raises(aiohttp.ClientResponseError):
                await provider.get_data('/test')

            mock_response.json.assert_not_awaited()

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='post',
    )
    async def test_post_data_success(
        self,
        mock_post: AsyncMock,
    ) -> None:
        """Тест успешного выполнения post - запроса.

        Args:
            mock_post: Мок метода aiohttp.ClientSession.post
        """
        expected = {'created': True}
        payload = {'name': 'Alex'}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json = AsyncMock(return_value=expected)

        mock_post.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)
            result = await provider.post_data('/create', data=payload)

        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(expected),
        )
        mock_post.assert_called_once_with('/create', json=payload)
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='post',
    )
    async def test_post_data_timeout(
        self,
        mock_post: AsyncMock,
    ) -> None:
        """Тест обработки таймаута при выполнении post - запроса.

        Args:
            mock_post: Мок метода aiohttp.ClientSession.post
        """
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = asyncio.TimeoutError()
        mock_response.json = AsyncMock()

        mock_post.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)

            with pytest.raises(asyncio.TimeoutError):
                await provider.post_data('/create')

            mock_response.json.assert_not_awaited()

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='delete',
    )
    async def test_delete_data_success(
        self,
        mock_delete: AsyncMock,
    ) -> None:
        """Тест успешного выполнения delete - запроса.

        Args:
            mock_delete: Мок метода aiohttp.ClientSession.delete
        """
        expected = {'deleted': True}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json = AsyncMock(return_value=expected)

        mock_delete.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)
            result = await provider.delete_data('/delete')

        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(expected),
        )
        mock_delete.assert_called_once_with('/delete')
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    @patch.object(
        target=aiohttp.ClientSession,
        attribute='delete',
    )
    async def test_delete_data_client_error(
        self,
        mock_delete: AsyncMock,
    ) -> None:
        """Тест обработки клиентской ошибки при выполнении delete - запроса.

        Args:
            mock_delete: Мок метода aiohttp.ClientSession.delete
        """
        err = aiohttp.ClientError()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = err
        mock_response.json = AsyncMock()

        mock_delete.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            provider = BaseProvider(session=session)

            with pytest.raises(aiohttp.ClientError):
                await provider.delete_data('/delete')

            mock_response.json.assert_not_awaited()
