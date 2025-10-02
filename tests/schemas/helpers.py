"""Фабрики данных для тестов Pydantic-схем опыта работы (experience)."""


def add_brackets(value: str) -> str:
    """Возвращает строку, обёрнутую в квадратные скобки.

    Args:
        value: Исходная строка

    Returns:
        str: Строка с добавленными квадратными скобками
    """
    return f'[{value}]'


def always_fails(value: str) -> str:  # noqa: D401
    """Всегда выбрасывает ValueError.

    Args:
        _: Строковый аргумент (не используется)

    Returns:
        str: Никогда не возвращает, всегда выбрасывает исключение

    Raises:
        ValueError: Всегда
    """
    raise ValueError('boom')
