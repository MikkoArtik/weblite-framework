"""Фабрики данных для тестов Pydantic-схем опыта работы (experience)."""

from typing import Any, Optional


def make_experience_create_data(
    resume_id: int = 1,
    company_name: str = 'Test Company',
    position: str = 'Test Position',
    start_date: str = '2021-01',
    end_date: Optional[str] = None,
    achievements: Optional[str] = None,
) -> dict[str, Any]:
    """Возвращает словарь данных для ExperienceCreateSchema.

    Args:
        resume_id: Идентификатор резюме (по умолчанию 1)
        company_name: Название компании (по умолчанию 'Test Company')
        position: Должность (по умолчанию 'Test Position')
        start_date: Дата начала работы (YYYY-MM, по умолчанию '2021-01')
        end_date: Дата окончания работы или None
        achievements: Доп. достижения

    Returns:
        dict: Словарь с данными для ExperienceCreateSchema
    """
    data: dict[str, Any] = {
        'resume_id': resume_id,
        'company_name': company_name,
        'position': position,
        'start_date': start_date,
    }
    if end_date is not None:
        data['end_date'] = end_date
    if achievements is not None:
        data['achievements'] = achievements
    return data


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
