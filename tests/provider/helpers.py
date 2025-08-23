"""Модуль вспомогательных классов и функций для тестов S3Provider."""

from typing import Any, AsyncIterator


class BytesBody:
    """Эмуляция resp['Body'] из boto: поддерживает async with и read()."""

    def __init__(self, *, data: bytes) -> None:
        """Сохраняет байты для последующего чтения.

        Args:
            data: Данные, которые должен вернуть метод read().
        """
        self._data = data

    async def __aenter__(self) -> 'BytesBody':
        """Возвращает self при входе в контекст.

        Returns:
            Текущий объект.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool:  # noqa: ANN001
        """Не подавляет исключения.

        Args:
            exc_type: Тип исключения.
            exc: Экземпляр исключения.
            tb: Traceback.

        Returns:
            False, чтобы исключение не подавлялось.
        """
        return False

    async def read(self) -> bytes:
        """Возвращает сохранённые байты.

        Returns:
            Сохранённые данные.
        """
        return self._data


async def aiter_pages(
    *, pages: list[dict[str, Any]]
) -> AsyncIterator[dict[str, Any]]:
    """Эмуляция работы paginator.paginate().

    Args:
        pages: Список страниц с ключами объектов.

    Yields:
        dict: Очередная страница с результатами.
    """
    for page in pages:
        yield page
