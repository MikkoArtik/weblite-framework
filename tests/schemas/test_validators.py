"""Модуль для тестирования общих валидаторов, используемых в сервисе."""

from datetime import date, datetime, timezone
from typing import Any, Callable, Optional

import pytest
from freezegun import freeze_time
from hamcrest import assert_that, equal_to

from weblite_framework.schemas.validators import (
    check_email_pattern,
    check_has_timezone,
    check_hidden_or_spaces,
    check_integer,
    check_length,
    check_no_double_spaces,
    check_no_html_scripts,
    check_not_empty,
    check_only_symbols,
    check_only_symbols_and_spaces,
    check_positive_num,
    check_russian_phone_number,
    check_symbols_numeric_spaces_special_char,
    parse_year_month_strict,
    skip_if_none,
)


class TestSkipIfNone:
    """Тесты для декоратора skip_if_none."""

    @pytest.mark.parametrize(
        argnames='inp, expected',
        argvalues=[
            (None, None),
            ('ok', '[ok]'),
        ],
    )
    def test_skip_if_none_basic(
        self,
        inp: str | None,
        expected: str | None,
    ) -> None:
        """Проверяет базовое поведение декоратора skip_if_none.

        Убеждается, что для None возвращается None,
        а для строки вызывается исходная функция.

        Args:
            inp: Входное значение
            expected: Ожидаемый результат после применения декоратора
        """
        # Вместо вызова add_brackets используем inline функцию
        def add_brackets_func(value: str) -> str:
            return f'[{value}]'

        wrapped = skip_if_none(func=add_brackets_func)
        assert_that(
            actual_or_assertion=wrapped(value=inp),
            matcher=equal_to(obj=expected),
        )

    def failing_validator(self, value: str) -> str:
        """Валидатор, который всегда выбрасывает исключение 'boom'."""
        raise ValueError('boom')


class TestSkipIfNoneIntegration:
    """Интеграционные проверки: существующие валидаторы с декоратором."""

    @pytest.mark.parametrize(
        argnames='func',
        argvalues=[
            check_not_empty,
            check_only_symbols_and_spaces,
            check_no_html_scripts,
            check_symbols_numeric_spaces_special_char,
            check_length,
        ],
    )
    def test_decorated_string_validators_accept_none(
        self,
        func: Callable[[Optional[str]], Optional[str]],
    ) -> None:
        """Проверяет, что строковые валидаторы с декоратором возвращают None.

        Args:
            func: Валидатор, обёрнутый в skip_if_none
        """
        result = func(None)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=None),
        )

    @pytest.mark.parametrize(
        argnames='func,value,expected, kwargs',
        argvalues=[
            (check_not_empty, ' x ', 'x', {}),
            (check_length, ' a ', 'a', {'max_length': 255}),
            (check_length, ' b ', 'b', {'max_length': 1000}),
            (check_only_symbols_and_spaces, '  Абв Гд  ', 'Абв Гд', {}),
            (check_no_html_scripts, '  plain  ', 'plain', {}),
            (check_symbols_numeric_spaces_special_char, '  Fo-1 ', 'Fo-1', {}),
        ],
    )
    def test_decorated_string_validators_process_non_none(
        self,
        func: Callable[..., Optional[str]],
        value: str,
        expected: str,
        kwargs: dict[str, object],
    ) -> None:
        """Проверяет обработку непустых значений у валидаторов с декоратором.

        Args:
            func: Валидатор, обёрнутый в skip_if_none
            value: Входная строка для проверки
            expected: Ожидаемый результат после валидации
            kwargs: Дополнительные аргументы для валидатора
        """
        result = func(value, **kwargs)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=expected),
        )


class TestCheckNotEmpty:
    """Тесты для валидатора check_not_empty."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Текст',
            ' N ',
        ],
    )
    def test_check_not_empty_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_not_empty возвращает строку.

        Проверяет, что check_not_empty возвращает строку,
        если она не пустая.

        Args:
            value: Текст, проходящий валидацию
        """
        result = check_not_empty(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    def test_check_not_empty_invalid(self) -> None:
        """Проверяет, что check_not_empty выбрасывает ValueError.

        Проверяет, что check_not_empty выбрасывает
        ValueError при пустой строке.

        Raises:
            ValueError: Если строка пустая.
        """
        value = ''
        with pytest.raises(expected_exception=ValueError):
            check_not_empty(value=value)


class TestCheckLength:
    """Тесты для универсального валидатора check_length."""

    @pytest.mark.parametrize(
        argnames='value, min_length, max_length, expected',
        argvalues=[
            ('A' * 255, 1, 255, 'A' * 255),
            (' A ', 1, 10, 'A'),
            ('', 0, 10, ''),
            ('   ', 0, 10, ''),
        ],
    )
    def test_check_length_valid(
        self,
        value: str,
        min_length: int,
        max_length: int,
        expected: str,
    ) -> None:
        """Проверяет успешную валидацию строк по длине.

        Args:
            value: Тестовая строка
            min_length: Минимальная допустимая длина
            max_length: Максимальная допустимая длина
            expected: Ожидаемый результат после trim
        """
        result = check_length(
            value=value,
            min_length=min_length,
            max_length=max_length,
        )
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=expected),
        )

    @pytest.mark.parametrize(
        argnames='value, min_length, max_length',
        argvalues=[
            ('', 1, 10),
            ('A' * 11, 1, 10),
            ('  ', 1, 10),
        ],
    )
    def test_check_length_invalid(
        self,
        value: str,
        min_length: int,
        max_length: int,
    ) -> None:
        """Проверяет, что check_length выбрасывает ValueError.

        Args:
            value: Тестовая строка
            min_length: Минимальная допустимая длина
            max_length: Максимальная допустимая длина

        Raises:
            ValueError: Если строка не удовлетворяет ограничениям
        """
        with pytest.raises(expected_exception=ValueError):
            check_length(
                value=value,
                min_length=min_length,
                max_length=max_length,
            )


class TestCheckOnlySymbols:
    """Тесты для валидатора check_only_symbols."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Строка',
            'String',
        ],
    )
    def test_check_only_symbols_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_only_symbols возвращает строку.

        Проверяет, что check_only_symbols возвращает строку,
        если она состоит только из символов (латиница/кириллица).

        Args:
            value: Текст, проходящий валидацию
        """
        result = check_only_symbols(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Строка String',
            'Строка!',
            '15587',
        ],
    )
    def test_check_only_symbols_invalid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_only_symbols выбрасывает ValueError.

        Данный метод проверяет, что check_only_symbols выбрасывает
        ValueError при передаче строки, состоящей не только
        из символов (латиница/кириллица).

        Args:
            value: Текст, проходящий валидацию

        Raises:
            ValueError: Если строка состоит не только из символов
        """
        with pytest.raises(expected_exception=ValueError):
            check_only_symbols(value=value)


class TestCheckOnlySymbolsAndSpaces:
    """Тесты для валидатора check_only_symbols_and_spaces."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Строка',
            'String and one more',
            '    String and one   ',
        ],
    )
    def test_check_only_symbols_and_spaces_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_only_symbols_and_spaces возвращает строку.

        Проверяет, что что check_only_symbols_and_spaces возвращает строку
        если она состоит только из символов (латиница/кириллица) и пробелов.

        Args:
            value: Текст, проходящий валидацию
        """
        result = check_only_symbols_and_spaces(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Строка_String',
            ' @ ',
            '15687',
        ],
    )
    def test_check_only_symbols_and_spaces_invalid(
        self,
        value: str,
    ) -> None:
        """Тест check_only_symbols_and_spaces с невалидными данными.

        Данный метод проверяет, что check_only_symbols_and_spaces выбрасывает
        ValueError при передаче строки, состоящей не только
        из символов (латиница/кириллица) и пробелов.

        Args:
            value: Текст, проходящий валидацию

        Raises:
            ValueError: Если строка состоит не только из символов и пробелов
        """
        with pytest.raises(expected_exception=ValueError):
            check_only_symbols_and_spaces(value=value)


class TestCheckEmailPattern:
    """Тесты для валидатора check_email_pattern."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'test@mail.space',
            'a_b@mail.com',
            'Name.Surname@ya.by',
        ],
    )
    def test_check_email_pattern_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_email_pattern возвращает строку.

        Проверяет, что check_email_pattern возвращает строку,
        если она соответствует шаблону email.

        Args:
            value: Email, проходящий валидацию
        """
        result = check_email_pattern(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            '@mail.space',
            '!a_%_b@mail.com',
            'Виталий@Пупкин.com',
        ],
    )
    def test_check_email_pattern_invalid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_email_pattern выбрасывает ValueError.

        Проверяет, что check_email_pattern выбрасывает
        ValueError при строке, которая не соответствует шаблону email.

        Args:
            value: Email, проходящий валидацию

        Raises:
            ValueError: Если строка не соответствует шаблону email
        """
        with pytest.raises(expected_exception=ValueError):
            check_email_pattern(value=value)


class TestCheckRussianPhoneNumber:
    """Тесты для валидатора check_russian_phone_number."""

    def test_check_russian_phone_number_valid(self) -> None:
        """Проверяет, что check_russian_phone_number возвращает строку.

        Проверяет, что check_russian_phone_number возвращает строку,
        если она соответствует шаблону мобильного номера телефона РФ.
        """
        value = '+70123456789'
        result = check_russian_phone_number(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            '+37523456789',
            '+7-0123-45678',
            '+7(0123)456789',
            '70123456789',
        ],
    )
    def test_check_russian_phone_number_invalid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_russian_phone_number выбрасывает ValueError.

        Проверяет, что check_russian_phone_number выбрасывает
        ValueError при строке, которая не соответствует
        шаблону мобильного номера телефона РФ.

        Args:
            value: Номер телефона, проходящий валидацию

        Raises:
            ValueError: Если номер телефона не соответствует шаблону
        """
        with pytest.raises(expected_exception=ValueError):
            check_russian_phone_number(value=value)


class TestCheckNoHTMLScripts:
    """Тесты для валидатора check_no_html_scripts."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Plain text',
            '< not a tag <',
            '',
        ],
    )
    def test_check_no_html_scripts_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_no_html_scripts возвращает строку.

        Проверяет, что check_no_html_scripts возвращает строку,
        если в ней не содержится html тегов и скриптов.

        Args:
            value: Текст, проходящий валидацию
        """
        result = check_no_html_scripts(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            '<script>alert()</script>',
            '</div>',
            'Before <br after> text',
        ],
    )
    def test_check_no_html_scripts_invalid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_no_html_scripts выбрасывает ValueError.

        Проверяет, что check_no_html_scripts выбрасывает
        ValueError при строке, которая содержит html теги/скрипты.

        Args:
            value: Текст, проходящий валидацию

        Raises:
            ValueError: Если строка содержит html теги/скрипты
        """
        with pytest.raises(expected_exception=ValueError):
            check_no_html_scripts(value=value)


class TestCheckHasTimezone:
    """Тесты для валидатора check_has_timezone."""

    def test_check_has_timezone_valid(self) -> None:
        """Проверяет, что check_has_timezone возвращает datetime.

        Проверяет, что check_has_timezone возвращает datetime,
        если в нем присутствует часовой пояс.
        """
        value = datetime(
            year=2020,
            month=12,
            day=31,
            hour=10,
            minute=10,
            tzinfo=timezone.utc,
        )
        result = check_has_timezone(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    def test_check_has_timezone_invalid(self) -> None:
        """Проверяет, что check_has_timezone выбрасывает ValueError.

        Проверяет, что check_has_timezone выбрасывает
        ValueError при datetime, которой не содержит часовой пояс.

        Raises:
            ValueError: Если datetime не содержит часовой пояс
        """
        with pytest.raises(expected_exception=ValueError):
            check_has_timezone(
                value=datetime(
                    year=2020,
                    month=12,
                    day=31,
                    hour=10,
                    minute=10,
                ),
            )


class TestCheckInteger:
    """Тесты для валидатора check_integer."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            0,
            1,
            -10,
            9999,
        ],
    )
    def test_check_integer_valid(self, value: int) -> None:
        """Проверяет, что check_integer возвращает целое число.

        Args:
            value: Целое число, проходящее валидацию
        """
        result = check_integer(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            1.5,
            '42',
            None,
            [],
            {},
        ],
    )
    def test_check_integer_invalid(self, value: int | Any) -> None:
        """Проверяет, что check_integer выбрасывает ValueError.

        Args:
            value: Некорректное значение

        Raises:
            ValueError: Если значение не int
        """
        with pytest.raises(expected_exception=ValueError):
            check_integer(value=value)


class TestCheckPositiveNum:
    """Тесты для валидатора check_positive_num."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            1,
            3.14,
            1000,
            0.0001,
        ],
    )
    def test_check_positive_num_valid(self, value: int | float) -> None:
        """Проверяет, что check_positive_num возвращает положительное число.

        Args:
            value: Положительное число
        """
        result = check_positive_num(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            0,
            -1,
            -3.5,
            '5',
            None,
            [],
        ],
    )
    def test_check_positive_num_invalid(
        self,
        value: int | float | Any,
    ) -> None:
        """Проверяет, что check_positive_num выбрасывает ValueError.

        Args:
            value: Некорректное значение (не число или неположительное)

        Raises:
            ValueError: Если число ≤ 0 или не число
        """
        with pytest.raises(expected_exception=ValueError):
            check_positive_num(value=value)


class TestCheckNoDoubleSpaces:
    """Тесты для валидатора check_no_double_spaces."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            ' text',
            'hello world ',
            ' a b c ',
            'one two three   ',
        ],
    )
    def test_check_no_double_spaces_valid(self, value: str) -> None:
        """Проверяет, что check_no_double_spaces возвращает строку.

        Args:
            value: Строка без двойных пробелов
        """
        result = check_no_double_spaces(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'hello  world',
            '  leading  double  spaces',
            'trailing  in',
            'in  the  middle',
        ],
    )
    def test_check_no_double_spaces_invalid(self, value: str | Any) -> None:
        """Проверяет, что check_no_double_spaces выбрасывает ValueError.

        Args:
            value: Строка с двойными пробелами

        Raises:
            ValueError: Если строка содержит два и более пробела подряд
        """
        with pytest.raises(expected_exception=ValueError):
            check_no_double_spaces(value=value)


class TestCheckSymbolsNumericSpacesSpecialChar:
    """Тесты для валидатора check_symbols_numeric_spaces_special_char."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Umbra GmbH',
            '№12: Foo-Bar (A/B), 3.5.',
            'Строка с числами 123 и знаками .,/-(): №',
            'simple / test - ok.',
        ],
    )
    def test_valid(self, value: str) -> None:
        """Проверяет, что валидные строки проходят валидацию.

        Args:
            value: Валидная строка
        """
        result = check_symbols_numeric_spaces_special_char(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'underscore_is_bad_',
            'bang!not allowed',
            'email@test.com?',
        ],
    )
    def test_invalid(self, value: str) -> None:
        """Проверяет, что невалидные строки вызывают ValueError.

        Args:
            value: Невалидная строка

        Raises:
            ValueError: Если встречаются неразрешённые символы
        """
        with pytest.raises(expected_exception=ValueError):
            check_symbols_numeric_spaces_special_char(value=value)


class TestCheckHiddenOrSpaces:
    """Тесты для валидатора check_hidden_or_spaces."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'no_spaces',
            'tabless',
            'newline',
        ],
    )
    def test_false(self, value: str) -> None:
        """Проверяет, что при отсутствии пробельных символов возвращает False.

        Args:
            value: Строка без пробельных символов
        """
        result = check_hidden_or_spaces(string=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=False),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'has space',
            'line\nbreak',
            'tab\there',
            ' start',
            'end ',
        ],
    )
    def test_true(self, value: str) -> None:
        """Проверяет, что при пробелах/скрытых символах возвращает True.

        Args:
            value: Строка с пробелами или скрытыми символами
        """
        result = check_hidden_or_spaces(string=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=True),
        )


class TestParseYearMonthStrict:
    """Тесты для валидатора parse_year_month_strict."""

    @pytest.mark.parametrize(
        argnames='value,expected',
        argvalues=[
            (
                '2020-01',
                date(year=2020, month=1, day=1),
            ),
            (
                '1999-12',
                date(year=1999, month=12, day=1),
            ),
        ],
    )
    def test_valid(self, value: str, expected: date) -> None:
        """Проверяет корректный парсинг формата YYYY-MM.

        Args:
            value: Входная строка
            expected: Ожидаемая дата
        """
        result = parse_year_month_strict(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=expected),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            '2020-13',
            '2020-00',
            '20-01',
            '2020/01',
            '2020-1',
            ' 2020-01',
            '2020-01 ',
        ],
    )
    def test_invalid_format(self, value: str) -> None:
        """Проверяет ошибки формата.

        Args:
            value: Некорректная строка

        Raises:
            ValueError: При несоответствии строгому формату YYYY-MM
        """
        with pytest.raises(expected_exception=ValueError):
            parse_year_month_strict(value=value)

    @freeze_time('2025-03-10')
    def test_future_month_invalid(self) -> None:
        """Проверяет, что будущая дата не допускается.

        Raises:
            ValueError: Если дата в будущем (после текущего месяца)
        """
        with pytest.raises(ValueError):
            parse_year_month_strict(value='2025-04')

    def test_year_too_small_invalid(self) -> None:
        """Проверяет нижнюю границу года (>= 1900).

        Raises:
            ValueError: Если год меньше 1900
        """
        with pytest.raises(expected_exception=ValueError):
            parse_year_month_strict(value='1899-12')