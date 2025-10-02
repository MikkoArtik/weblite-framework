"""Модуль для тестирования общих валидаторов."""

from datetime import date, datetime, timezone
from typing import Any

import pytest
from hamcrest import assert_that, equal_to, none

from weblite_framework.schemas.validators import (
    check_email_pattern,
    check_empty_to_none,
    check_has_timezone,
    check_integer,
    check_max_length_255,
    check_max_length_1000,
    check_no_double_spaces,
    check_no_html_scripts,
    check_not_empty,
    check_only_symbols,
    check_only_symbols_and_spaces,
    check_positive_num,
    check_russian_phone_number,
    validate_birth_date,
    validate_filename,
    validate_graduation_year,
    validate_telegram_nickname,
    validate_title_symbols,
)


class TestValidateFilename:
    """Тесты для валидатора validate_filename."""

    def test_validate_filename_valid(self) -> None:
        """Проверяет, что validate_filename возвращает строку."""
        value = 'test.txt'
        result = validate_filename(filename=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    def test_validate_filename_invalid(self) -> None:
        """Проверяет, что validate_filename выбрасывает ValueError."""
        value = ''
        with pytest.raises(expected_exception=ValueError):
            validate_filename(filename=value)


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
        """Проверяет, что check_not_empty возвращает строку."""
        result = check_not_empty(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    def test_check_not_empty_invalid(self) -> None:
        """Проверяет, что check_not_empty выбрасывает ValueError."""
        value = ''
        with pytest.raises(expected_exception=ValueError):
            check_not_empty(value=value)


class TestCheckMaxLength255:
    """Тесты для валидатора check_max_length_255."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'A' * 255,
            'A',
            '    ',
            '',
        ],
    )
    def test_check_max_length_255_valid(
        self,
        value: str,
    ) -> None:
        """Проверяет, что check_max_length_255 возвращает строку."""
        result = check_max_length_255(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    def test_check_max_length_255_invalid(self) -> None:
        """Проверяет, что check_max_length_255 выбрасывает ValueError."""
        value = 'A' * 256
        with pytest.raises(expected_exception=ValueError):
            check_max_length_255(value=value)


class TestCheckMaxLength1000:
    """Тесты для валидатора check_max_length_1000."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'A' * 1000,
            'A',
            '',
            '    ',
        ],
    )
    def test_check_max_length_1000_valid(
        self,
        value: str,
    ) -> None:
        """Тест check_max_length_1000 с валидными данными."""
        result = check_max_length_1000(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    def test_check_max_length_1000_invalid(self) -> None:
        """Тест check_max_length_1000 с невалидными данными."""
        value = 'A' * 1001
        with pytest.raises(expected_exception=ValueError):
            check_max_length_1000(value=value)


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
        """Проверяет, что check_only_symbols возвращает строку."""
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
        """Проверяет, что check_only_symbols выбрасывает ValueError."""
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
        """Проверяет, что check_only_symbols_and_spaces возвращает строку."""
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
        """Тест check_only_symbols_and_spaces с невалидными данными."""
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
        """Проверяет, что check_email_pattern возвращает строку."""
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
        """Проверяет, что check_email_pattern выбрасывает ValueError."""
        with pytest.raises(expected_exception=ValueError):
            check_email_pattern(value=value)


class TestCheckRussianPhoneNumber:
    """Тесты для валидатора check_russian_phone_number."""

    def test_check_russian_phone_number_valid(self) -> None:
        """Проверяет, что check_russian_phone_number возвращает строку."""
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
        """Проверяет, что check_russian_phone_number выбрасывает ValueError."""
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
        """Проверяет, что check_no_html_scripts возвращает строку."""
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
        """Проверяет, что check_no_html_scripts выбрасывает ValueError."""
        with pytest.raises(expected_exception=ValueError):
            check_no_html_scripts(value=value)


class TestCheckHasTimezone:
    """Тесты для валидатора check_has_timezone."""

    def test_check_has_timezone_valid(self) -> None:
        """Проверяет, что check_has_timezone возвращает datetime."""
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
        """Проверяет, что check_has_timezone выбрасывает ValueError."""
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
        """Проверяет, что check_integer возвращает целое число."""
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
        """Проверяет, что check_integer выбрасывает ValueError."""
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
        """Проверяет, что check_positive_num возвращает положительное число."""
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
        """Проверяет, что check_positive_num выбрасывает ValueError."""
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
        """Проверяет, что check_no_double_spaces возвращает строку."""
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
        """Проверяет, что check_no_double_spaces выбрасывает ValueError."""
        with pytest.raises(expected_exception=ValueError):
            check_no_double_spaces(value=value)


class TestCheckEmptyToNone:
    """Тесты для валидатора check_empty_to_none."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=['', '   ', None],
    )
    def test_check_empty_to_none_returns_none(
        self,
        value: str | None,
    ) -> None:
        """Проверяет, что пустые значения преобразуются в None."""
        result = check_empty_to_none(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=none(),
        )

    @pytest.mark.parametrize(
        argnames=[
            'value',
            'expected',
        ],
        argvalues=[
            (
                'https://example.com/p.jpg',
                'https://example.com/p.jpg',
            ),
            (
                '  https://example.com/p.jpg  ',
                'https://example.com/p.jpg',
            ),
            (
                'a b',
                'a b',
            ),
        ],
    )
    def test_check_empty_to_none_trims_non_empty(
        self,
        value: str,
        expected: str,
    ) -> None:
        """Проверяет, что непустые строки возвращаются с обрезанными краями."""
        result = check_empty_to_none(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=expected),
        )


class TestValidateGraduationYear:
    """Тесты для валидатора validate_graduation_year."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[1990, 2000, 2023],
    )
    def test_validate_graduation_year_valid(self, value: int) -> None:
        """Проверяет, что validate_graduation_year возвращает год."""
        result = validate_graduation_year(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[1899, 0, -1],
    )
    def test_validate_graduation_year_invalid_less_than_1900(
        self, value: int
    ) -> None:
        """Проверяет, что validate_graduation_year выбрасывает.

        ValueError для года < 1900.
        """
        with pytest.raises(expected_exception=ValueError):
            validate_graduation_year(value=value)

    def test_validate_graduation_year_invalid_future(self) -> None:
        """Проверяет, что validate_graduation_year выбрасывает.

        ValueError для будущего года.
        """
        future_year = date.today().year + 1
        with pytest.raises(expected_exception=ValueError):
            validate_graduation_year(value=future_year)


class TestValidateBirthDate:
    """Тесты для валидатора validate_birth_date."""

    def test_validate_birth_date_valid(self) -> None:
        """Проверяет, что validate_birth_date возвращает дату."""
        value = date(1990, 1, 1)
        result = validate_birth_date(birthday=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    def test_validate_birth_date_invalid_future(self) -> None:
        """Проверяет, что validate_birth_date выбрасывает.

        ValueError для будущей даты.
        """
        future_date = date.today().replace(year=date.today().year + 1)
        with pytest.raises(expected_exception=ValueError):
            validate_birth_date(birthday=future_date)

    def test_validate_birth_date_invalid_young(self) -> None:
        """Проверяет, что validate_birth_date выбрасывает.

        ValueError для возраста < 16 лет.
        """
        young_date = date.today().replace(year=date.today().year - 15)
        with pytest.raises(expected_exception=ValueError):
            validate_birth_date(birthday=young_date)


class TestValidateTelegramNickname:
    """Тесты для валидатора validate_telegram_nickname."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=['@username', '@test123', '@user_name'],
    )
    def test_validate_telegram_nickname_valid(self, value: str) -> None:
        """Проверяет, что validate_telegram_nickname возвращает никнейм."""
        result = validate_telegram_nickname(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=['@usr', 'user', '@user@name', '@user!name'],
    )
    def test_validate_telegram_nickname_invalid(self, value: str) -> None:
        """Проверяет, что validate_telegram_nickname выбрасывает ValueError."""
        with pytest.raises(expected_exception=ValueError):
            validate_telegram_nickname(value=value)


class TestValidateTitleSymbols:
    """Тесты для валидатора validate_title_symbols."""

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Резюме разработчика',
            'Resume Title 1.0',
            'Title (with) brackets',
            'Title with/slash',
        ],
    )
    def test_validate_title_symbols_valid(self, value: str) -> None:
        """Проверяет, что validate_title_symbols возвращает строку."""
        result = validate_title_symbols(value=value)
        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=value.strip()),
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=[
            'Title with @ symbol',
            'Title with ! symbol',
            'Title with _ underscore',
        ],
    )
    def test_validate_title_symbols_invalid(self, value: str) -> None:
        """Проверяет, что validate_title_symbols выбрасывает ValueError."""
        with pytest.raises(expected_exception=ValueError):
            validate_title_symbols(value=value)
