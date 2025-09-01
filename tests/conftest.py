"""Фикстуры для тестов weblite-framework."""

import pytest

from tests.helpers import TestDTO, TestModel


@pytest.fixture(scope='function')
def test_dto() -> TestDTO:
    """Фикстура для тестового DTO."""
    return TestDTO(id_=1, name='test')


@pytest.fixture(scope='function')
def test_model() -> TestModel:
    """Фикстура для тестовой модели."""
    return TestModel(id_=1, name='test')
