"""Тесты для конфигурационных настроек базы данных."""

import pytest
from hamcrest import assert_that, equal_to
from pydantic import ValidationError

from weblite_framework.settings.database import ASYNC_DRIVER, DatabaseSettings


class TestDatabaseSettings:
    """Класс тестов конфигурационных настроек базы данных."""

    def test_initialization_from_environment_variables(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Проверка инициализации настроек из переменных окружения."""
        monkeypatch.setenv('db_internal_port', '1111')
        monkeypatch.setenv('db_external_port', '2222')
        monkeypatch.setenv('postgres_user', 'user')
        monkeypatch.setenv('postgres_password', 'password')
        monkeypatch.setenv('postgres_host', 'host')
        monkeypatch.setenv('postgres_db', 'name')

        settings = DatabaseSettings()

        assert_that(
            actual_or_assertion=settings.internal_port,
            matcher=equal_to(1111),
        )
        assert_that(
            actual_or_assertion=settings.external_port,
            matcher=equal_to(2222),
        )
        assert_that(
            actual_or_assertion=settings.user,
            matcher=equal_to(obj='user'),
        )
        assert_that(
            actual_or_assertion=settings.password,
            matcher=equal_to(obj='password'),
        )
        assert_that(
            actual_or_assertion=settings.host,
            matcher=equal_to(obj='host'),
        )
        assert_that(
            actual_or_assertion=settings.db_name,
            matcher=equal_to(obj='name'),
        )

    def test_db_url_property_builds(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Проверка формирования строки подключения db_url."""
        monkeypatch.setenv('db_internal_port', '1111')
        monkeypatch.setenv('db_external_port', '2222')
        monkeypatch.setenv('postgres_user', 'user')
        monkeypatch.setenv('postgres_password', 'password')
        monkeypatch.setenv('postgres_host', 'host')
        monkeypatch.setenv('postgres_db', 'name')

        settings = DatabaseSettings()

        expected = f'{ASYNC_DRIVER}://user:password@host:1111/name'

        assert_that(
            actual_or_assertion=settings.db_url,
            matcher=equal_to(obj=expected),
        )

    def test_missing_required_variable(self) -> None:
        """Проверка ошибки при отсутствии обязательной переменной окружения."""
        with pytest.raises(ValidationError):
            DatabaseSettings()
