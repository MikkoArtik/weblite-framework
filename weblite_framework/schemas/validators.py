"""Модуль с кастомными валидаторами для проекта."""

import re
from datetime import date, datetime

__all__ = [
    'validate_filename',
    'check_not_empty',
    'check_max_length_255',
    'check_max_length_1000',
    'check_only_symbols',
    'check_only_symbols_and_spaces',
    'check_email_pattern',
    'check_russian_phone_number',
    'check_no_html_scripts',
    'check_has_timezone',
    'check_integer',
    'check_positive_num',
    'check_no_double_spaces',
    'check_empty_to_none',
    'validate_graduation_year',
    'validate_birth_date',
    'validate_telegram_nickname',
    'validate_title_symbols',
]


def validate_filename(filename: str) -> str:
    """Проверяет, что имя файла непустое.

    Args:
        filename: Имя файла.

    Returns:
        str: То же имя файла, если проверка пройдена

    Raises:
        ValueError: Если имя файла пустое.
    """
    if not filename:
        raise ValueError('filename is required')
    return filename


def check_not_empty(value: str) -> str:
    """Проверяет поле на пустое значение.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if not value or value.strip() == '':
        raise ValueError('Поле не может быть пустым')
    return value.strip()


def check_max_length_255(value: str) -> str:
    """Проверяет поле на длину не более 255 символов.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if value and len(value.strip()) > 255:
        raise ValueError('Длина поля не должна превышать 255 символов')
    return value.strip()


def check_max_length_1000(value: str) -> str:
    """Проверяет поле на длину не более 1000 символов.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if value and len(value.strip()) > 1000:
        raise ValueError('Длина поля не должна превышать 1000 символов')
    return value.strip()


def check_only_symbols(value: str) -> str:
    """Проверяет поле на наличие только символов (латиница/кириллица).

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    pattern = r'^[a-zA-Zа-яА-яеЁ]+$'
    if value and not re.fullmatch(
        pattern=pattern,
        string=value,
    ):
        raise ValueError(
            'Поле может состоять только из букв (латиница/кириллица)',
        )
    return value


def check_only_symbols_and_spaces(value: str) -> str:
    """Проверяет поле на наличие символов (латиница/кириллица) и пробелов.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    pattern = r'^[a-zA-Zа-яА-ЯеЁ\s]+$'
    if value and not re.fullmatch(
        pattern=pattern,
        string=value,
    ):
        raise ValueError(
            'Поле может состоять только из букв (латиница/кириллица) '
            'и пробелов',
        )
    return value.strip()


def check_email_pattern(value: str) -> str:
    """Проверяет email на соответствие шаблону электронной почты.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    pattern = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    if not re.match(
        pattern=pattern,
        string=value,
    ):
        raise ValueError('Неверный формат email')
    return value


def check_russian_phone_number(value: str) -> str:
    """Проверяет номер телефона на соответствие телефона РФ.

    Args:
        value: Проверяемые данные

    Returns:
        value: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if value:
        pattern = r'^\+7([\d]{10})$'
        if not (
            re.fullmatch(
                pattern=pattern,
                string=value,
            )
        ):
            raise ValueError(
                'Неверный формат номера телефона. Формат: +7XXXXXXXXXX',
            )
    return value


def check_no_html_scripts(value: str) -> str:
    """Проверяет наличие html скриптов.

    Args:
        value: Проверяемые данные

    Returns:
        text: Данные, прошедшие валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    html_pattern = re.compile(
        pattern=r'<\s*[a-z][\s\S]*>|</\s*[a-z][\s\S]*>',
        flags=re.IGNORECASE,
    )
    if value and html_pattern.search(value):
        raise ValueError('Текст должен быть без HTML/скриптов')
    return value.strip()


def check_has_timezone(value: datetime) -> datetime:
    """Проверяет, что значение datetime содержит информацию о таймзоне.

    Args:
        value: Дата и время

    Returns:
        datetime: То же значение, если проверка пройдена

    Raises:
        ValueError: Если отсутствует tzinfo
    """
    if value and value.tzinfo is None:
        raise ValueError('Дата и время должны содержать таймзону (tzinfo)')
    return value


def check_integer(value: int) -> int:
    """Проверяет, что значение является целым числом.

    Args:
        value: Проверяемое значение

    Returns:
        int: то же число

    Raises:
        ValueError: Значение должно целым числом
    """
    if not isinstance(value, int):
        raise ValueError('Значение должно быть целым числом')
    return value


def check_positive_num(value: int | float) -> int | float:
    """Проверяет, что значение является положительным числом.

    Args:
        value: Проверяемое значение

    Returns:
        int | float: то же число

    Raises:
        ValueError: Если значение не число или не положительное
    """
    if not isinstance(value, (int, float)):
        raise ValueError('Значение должно быть числом')
    if value <= 0:
        raise ValueError('Значение должно быть больше нуля')
    return value


def check_no_double_spaces(value: str) -> str:
    """Проверяет, что в строке нет двух и более пробелов подряд.

    Args:
        value: Проверяемая строка

    Returns:
        str: Та же строка, если проверка пройдена

    Raises:
        ValueError: Если внутри строки встречаются два и более пробела подряд
    """
    value = value.strip()
    if '  ' in value:
        raise ValueError(
            'Строка не может содержать более 2 пробелов подряд',
        )
    return value


def check_empty_to_none(value: str | None) -> str | None:
    """Пустая строка преобразуется в None, непустая — strip().

    Args:
        value: Проверяемые данные

    Returns:
        str | None: None для пустых значений, иначе — strip() обрезанная строка
    """
    if value is None:
        return None
    s = value.strip()
    return None if s == '' else s


def validate_graduation_year(value: int) -> int:
    """Проверяет год окончания учебного заведения на корректность.

    Args:
        value: Проверяемый год

    Returns:
        int: Год, прошедший валидацию

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if not value or value < 1900:
        raise ValueError('Год окончания не может быть меньше 1900')
    if value > date.today().year:
        raise ValueError('Год окончания не может быть в будущем')
    return value


def validate_birth_date(birthday: date) -> date:
    """Проверяет дату рождения на корректность.

    Args:
        birthday: Проверяемая дата рождения

    Returns:
        date: Дата рождения

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    today = date.today()
    if birthday > today:
        raise ValueError('Дата рождения не может быть в будущем')

    age_delta = (today.month, today.day) < (birthday.month, birthday.day)
    age = today.year - birthday.year - age_delta

    if age < 16:
        raise ValueError('Возраст должен быть не младше 16 лет')
    return birthday


def validate_telegram_nickname(value: str) -> str:
    """Проверяет Telegram-ник на соответствие шаблону.

    Args:
        value: Проверяемый никнейм

    Returns:
        str: Прошедший валидацию Telegram-ник

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    if value:
        pattern = r'^@[\da-zA-Z_]+$'
        if len(value) < 5:
            raise ValueError(
                'Telegram-ник должен быть не короче 5 символов',
            )
        if len(value) > 32:
            raise ValueError(
                'Telegram-ник должен быть не длиннее 32 символов',
            )
        if not re.fullmatch(pattern=pattern, string=value):
            raise ValueError(
                'Неверный формат. Должен начинаться с @, '
                'допустимы буквы, цифры, нижнее подчёркивание.',
            )
    return value


def validate_title_symbols(value: str) -> str:
    """Проверяет название резюме на допустимые символы.

    Допустимые символы: буквы, цифры, пробелы и [. , / - ( ) № :]

    Args:
        value: Проверяемое название резюме

    Returns:
        str: Прошедшее валидацию название

    Raises:
        ValueError: Ошибка в случае непрохождения валидации
    """
    value = value.strip()

    pattern = r'^[a-zA-Zа-яА-ЯёЁ0-9\s.,/\-\(\)№:]+$'
    if not re.fullmatch(pattern=pattern, string=value):
        raise ValueError(
            'Название резюме может содержать только буквы '
            '(латиница/кириллица), цифры, пробелы и спецсимволы: '
            '[. , / - ( ) № :]'
        )

    return value
