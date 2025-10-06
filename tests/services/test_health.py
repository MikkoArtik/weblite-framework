"""Тесты для сервиса проверки работоспособности."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from weblite_framework.exceptions.service import DatabaseConnectionError
from weblite_framework.repository.common import CommonRepo
from weblite_framework.services.health import HealthService


class TestHealthService:
    """Тесты для сервиса HealthService."""

    @patch.object(
        target=CommonRepo,
        attribute='_is_connection_exist',
        new_callable=AsyncMock,
    )
    async def test_check_db_connection_success(
        self,
        is_connection_exist_mock: AsyncMock,
    ) -> None:
        """Проверка успешного соединения с БД.

        Args:
            is_connection_exist_mock: Мок метода _is_connection_exist.
        """
        mock_session = AsyncMock(spec=AsyncSession)
        is_connection_exist_mock.return_value = True

        service = HealthService(session=mock_session)
        await service.check_db_connection()

    @patch.object(
        target=CommonRepo,
        attribute='_is_connection_exist',
        new_callable=AsyncMock,
    )
    async def test_check_db_connection_failed(
        self,
        is_connection_exist_mock: AsyncMock,
    ) -> None:
        """Проверка неудачного соединения с БД.

        Args:
            is_connection_exist_mock: Мок метода _is_connection_exist.
        """
        mock_session = AsyncMock(spec=AsyncSession)
        is_connection_exist_mock.return_value = False

        service = HealthService(session=mock_session)

        with pytest.raises(DatabaseConnectionError):
            await service.check_db_connection()
