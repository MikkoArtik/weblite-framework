"""Настройки для подключения к базе данных PostgreSQL."""

from pydantic import Field
from pydantic_settings import BaseSettings

__all__ = ['DatabaseSettings']

ASYNC_DRIVER = 'postgresql+asyncpg'


class DatabaseSettings(BaseSettings):
    """Конфигурация подключения к PostgreSQL.

    Args:
        internal_port: Внутренний порт (используется внутри Docker-сети).
        external_port: Внешний порт (используется для подключения с хоста).
        user: Имя пользователя.
        password: Пароль пользователя.
        host: Хост.
        db_name: Имя базы данных.
    """

    internal_port: int = Field(alias='db_internal_port')
    external_port: int = Field(alias='db_external_port')

    user: str = Field(alias='postgres_user')
    password: str = Field(alias='postgres_password')
    host: str = Field(alias='postgres_host')
    db_name: str = Field(alias='postgres_db')

    @property
    def db_url(self) -> str:
        """URL для асинхронного подключения к PostgreSQL внутри Docker-сети.

        Returns:
            str: Строка подключения.
        """
        return (
            f'{ASYNC_DRIVER}://{self.user}:'
            f'{self.password}@{self.host}:'
            f'{self.internal_port}/{self.db_name}'
        )
