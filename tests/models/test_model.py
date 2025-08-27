"""Модуль с тестами для базовой пользовательской Pydantic модели."""

import pytest
from hamcrest import assert_that, equal_to, has_entries
from pydantic import Field

from tests.models.helpers import UserSchemaExample
from weblite_framework.schemas.base import CustomBaseModel


class TestCustomModels:
    """Тестируется базовый класс CustomBaseModel."""

    def test_valid_schema(self) -> None:
        """Проверяет метод generate_example() Pydantic модели.

        Создаёт корректный экземпляр модели и проверяет,
        что значения полей и алиасы заданы верно.
        """
        obj = UserSchemaExample.generate_example()
        assert_that(
            actual_or_assertion=obj.id_,
            matcher=equal_to(1),
        )
        assert_that(
            actual_or_assertion=obj.email,
            matcher=equal_to('a@b.c'),
        )

        data_by_alias = obj.model_dump(
            by_alias=True,
        )
        assert_that(
            actual_or_assertion=data_by_alias,
            matcher=has_entries(
                {
                    'id': 1,
                    'email': 'a@b.c',
                },
            ),
        )

    def test_missing_alias_raises_type_error(self) -> None:
        """Проверяет поведение модели без alias у поля.

        Raises:
            TypeError: Если поле модели объявлено без alias.
        """
        with pytest.raises(expected_exception=TypeError):

            class NotAlias(CustomBaseModel):
                id_: int = Field(
                    description='ID',
                    examples=[1],
                )

    def test_missing_description_raises_type_error(self) -> None:
        """Проверяет поведение модели без description у поля.

        Raises:
            TypeError: Если поле модели объявлено без description.
        """
        with pytest.raises(expected_exception=TypeError):

            class NotDescription(CustomBaseModel):
                id_: int = Field(
                    alias='id',
                    examples=[1],
                )

    def test_missing_examples_raises_type_error(self) -> None:
        """Проверяет поведение модели без examples у поля.

        Raises:
            TypeError: Если поле модели объявлено без examples.
        """
        with pytest.raises(expected_exception=TypeError):

            class NotExamples(CustomBaseModel):
                id_: int = Field(
                    alias='id',
                    description='ID',
                )

    def test_examples_multi_value(self) -> None:
        """Проверяет поведение модели при множественных examples.

        Raises:
            TypeError: Если в examples указано более одного значения.
        """
        with pytest.raises(expected_exception=TypeError):

            class MultiExamples(CustomBaseModel):
                id_: int = Field(
                    alias='id',
                    description='ID',
                    examples=[1, 2],
                )
