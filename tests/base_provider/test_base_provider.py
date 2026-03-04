"""Модуль для тестов класса BaseProvider."""

from http import HTTPMethod
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aiohttp import ClientSession
from hamcrest import assert_that, contains_string, equal_to

from weblite_framework.exceptions.auth import UnauthorizedException
from weblite_framework.exceptions.base import BaseAppException
from weblite_framework.provider.base_provider import BaseProvider


class TestBaseProvider:
    """Набор юнит-тестов для BaseProvider."""

    @pytest.mark.parametrize(
        'method',
        [HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.DELETE],
    )
    @pytest.mark.parametrize(
        'params,data,headers',
        [
            pytest.param(None, None, None, id='empty_request'),
            pytest.param(
                {'include': 'profile'}, None, None, id='query_params'
            ),
            pytest.param(
                None,
                {
                    'name': 'Елена',
                    'email': 'elena.kuznetsovaa@example.com',
                },
                None,
                id='body_data',
            ),
            pytest.param(
                None,
                None,
                {'Authorization': 'Bearer test-token'},
                id='auth_header',
            ),
            pytest.param(
                {'include': 'profile'},
                {
                    'name': 'Елена',
                    'email': 'elena.kuznetsovaa@example.com',
                },
                {'Authorization': 'Bearer test-token'},
                id='full_request',
            ),
        ],
    )
    @patch.object(ClientSession, 'request')
    async def test_create_request_success(
        self,
        mock_request: MagicMock,
        provider: BaseProvider,
        path: str,
        method: HTTPMethod,
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
        headers: dict[str, str] | None,
    ) -> None:
        """Проверяет успешное создание запроса.

        Args:
            mock_request: мок метода ClientSession.request
            provider: BaseProvider
            path: адрес эндпоинта
            method: тип запроса
            params: параметры запроса
            data: тело запроса
            headers: необязательные заголовки запроса
        """
        response = MagicMock()
        response.status = 200
        response.json = AsyncMock(return_value={'ok': True})

        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=response)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_request.return_value = cm

        with patch.object(
            provider,
            'check_response_status',
            new=AsyncMock(return_value=None),
        ) as mock_check_status:
            result = await provider._create_request(
                method=method,
                path=path,
                params=params,
                data=data,
                headers=headers,
            )

        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj={'ok': True}),
        )

        mock_request.assert_called_once()

        _, kwargs = mock_request.call_args
        assert_that(
            actual_or_assertion=kwargs['method'],
            matcher=equal_to(obj=method),
        )
        assert_that(
            actual_or_assertion=kwargs['url'],
            matcher=equal_to(obj=path),
        )
        assert_that(
            actual_or_assertion=kwargs['params'],
            matcher=equal_to(obj=params),
        )
        assert_that(
            actual_or_assertion=kwargs['data'],
            matcher=equal_to(obj=data),
        )
        assert_that(
            actual_or_assertion=kwargs['headers'],
            matcher=equal_to(obj=headers),
        )

        mock_check_status.check_response_status.assert_awaited_once()

    @patch.object(ClientSession, 'request')
    async def test_create_request_no_payload(
        self,
        mock_request: MagicMock,
        provider: BaseProvider,
        path: str,
    ) -> None:
        """Проверяет {} при отсутствии payload.

        Args:
            mock_request: мок метода ClientSession.request
            provider: BaseProvider
            path: адрес эндпоинта
        """
        response = MagicMock()
        response.status = 200
        response.json = AsyncMock(return_value=None)

        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=response)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_request.return_value = cm

        with patch.object(
            provider,
            'check_response_status',
            new=AsyncMock(return_value=None),
        ):
            result = await provider._create_request(
                method=HTTPMethod.GET,
                path=path,
            )

        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj={}),
        )

    @patch.object(ClientSession, 'request')
    async def test_create_request_error_503(
        self,
        mock_request: MagicMock,
        provider: BaseProvider,
        path: str,
    ) -> None:
        """Проверяет ошибку 503 при ClientError.

        Args:
            mock_request: мок метода ClientSession.request
            provider: BaseProvider
            path: адрес эндпоинта
        """
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(
            side_effect=aiohttp.ClientError('Ошибка соединения')
        )
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_request.return_value = cm

        with pytest.raises(BaseAppException) as exc_info:
            await provider._create_request(method=HTTPMethod.GET, path=path)

        err: BaseAppException = exc_info.value

        assert_that(
            actual_or_assertion=err.status_code,
            matcher=equal_to(obj=503),
        )
        assert_that(
            actual_or_assertion=err.detail,
            matcher=contains_string('Ошибка доступа к сервису'),
        )

    async def test_status_401(
        self,
        provider: BaseProvider,
    ) -> None:
        """Проверяет статус 401 UnauthorizedException.

        Args:
            provider: BaseProvider
        """
        response = MagicMock()
        response.status = 401

        with pytest.raises(UnauthorizedException) as exc:
            await provider.check_response_status(response=response)

        assert_that(
            actual_or_assertion=exc.value.status_code,
            matcher=equal_to(401),
        )
        assert_that(
            actual_or_assertion=exc.value.detail,
            matcher=contains_string('401'),
        )

    async def test_status_503(
        self,
        provider: BaseProvider,
    ) -> None:
        """Проверяет статус 503 BaseAppException.

        Args:
            provider: BaseProvider
        """
        response = MagicMock()
        response.status = 503

        with pytest.raises(BaseAppException) as exc:
            await provider.check_response_status(response=response)

        assert_that(
            actual_or_assertion=exc.value.status_code,
            matcher=equal_to(503),
        )
        assert_that(
            actual_or_assertion=exc.value.detail,
            matcher=contains_string('503'),
        )

    async def test_status_200(
        self,
        provider: BaseProvider,
    ) -> None:
        """Проверяет статус 200 Success.

        Args:
            provider: BaseProvider
        """
        response = MagicMock()
        response.status = 200

        await provider.check_response_status(response=response)
