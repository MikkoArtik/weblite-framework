"""Тесты для базового репозитория."""

from unittest.mock import AsyncMock, patch

import pytest
from hamcrest import assert_that, equal_to, greater_than_or_equal_to, is_
from sqlalchemy.exc import InterfaceError

from tests.helpers import TestModel, TestRepository, initialize_invalid_class
from tests.repository.helpers import SampleRepo


class TestBaseRepository:
    """Класс тестов базового репозитория."""

    def test_initialization(self) -> None:
        """Проверка инициализации базового репозитория.

        Данный тест проверяет корректное присвоение сессии
        при создании экземпляра репозитория.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        # Проверяем, что сессия правильно присвоена
        assert_that(
            actual_or_assertion=repo.session,
            matcher=equal_to(obj=session),
        )

    def test_abstract_methods_not_implemented(self) -> None:
        """Проверка что абстрактные методы не реализованы.

        Данный тест проверяет, что при вызове неимплементированного
        абстрактного метода вызывается NotImplementedError.
        """
        session = AsyncMock()

        # Проверяем, что при создании экземпляра класса с неимплементированным
        # абстрактным методом вызывается TypeError
        with pytest.raises(expected_exception=TypeError):
            initialize_invalid_class(session=session)

    def test_add(self, test_model: TestModel) -> None:
        """Проверка метода add.

        Данный тест проверяет вызов метода add у сессии
        при добавлении экземпляра модели.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        repo.add(instance=test_model)

        # Проверяем, что метод add был вызван с правильным аргументом
        session.add.assert_called_once_with(test_model)

    async def test_commit(self) -> None:
        """Проверка метода commit.

        Данный тест проверяет вызов метода commit у сессии
        для сохранения изменений в базе данных.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        await repo.commit()

        # Проверяем, что метод commit был вызван
        session.commit.assert_called_once()

    async def test_flush(self) -> None:
        """Проверка метода flush.

        Данный тест проверяет вызов метода flush у сессии
        для сброса изменений без коммита.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        await repo.flush()

        # Проверяем, что метод flush был вызван
        session.flush.assert_called_once()

    async def test_add_record(self, test_model: TestModel) -> None:
        """Проверка метода _add_record.

        Данный тест проверяет вызов корректных методов у экземпляра
        сессии для создания экземпляра объекта.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        result = await repo._add_record(model=test_model)

        assert_that(
            actual_or_assertion=result,
            matcher=equal_to(obj=test_model),
        )
        # Проверяем, что методы сессии были вызваны с правильными аргументами
        session.add.assert_called_once_with(test_model)
        session.flush.assert_called_once()

    async def test_update(self) -> None:
        """Проверка метода _update.

        Данный тест проверяет изменение полей у передаваемой модели.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)
        existing_model = TestModel(id_=1, name='old_name')
        new_data = TestModel(id_=1, name='new_name')

        result = await repo._update(
            existing_model=existing_model,
            new_data=new_data,
        )

        assert_that(
            actual_or_assertion=result.name,
            matcher=equal_to(obj=new_data.name),
        )
        assert_that(
            actual_or_assertion=result.id_,
            matcher=equal_to(obj=existing_model.id_),
        )
        # Проверяем, что метод flush был вызван
        session.flush.assert_called_once()

    async def test_update_with_ignore_fields(self) -> None:
        """Проверка метода _update с передачей аргумента ignore_fields.

        Данный тест проверяет, что метод _update не изменяет значение поля
        у передаваемой модели, если данное поле добавлено в игнор-лист.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)
        existing_model = TestModel(id_=1, name='old_name')
        new_data = TestModel(
            id_=2,  # Должно быть проигнорировано
            name='new_name',
        )

        result = await repo._update(
            existing_model=existing_model,
            new_data=new_data,
            ignore_fields=['id_'],  # Явно указываем игнорируемое поле
        )

        assert_that(
            actual_or_assertion=result.name,
            matcher=equal_to(obj=new_data.name),
        )
        assert_that(
            actual_or_assertion=result.id_,
            matcher=equal_to(
                obj=existing_model.id_,
            ),  # ID не должен измениться
        )
        # Проверяем, что метод flush был вызван
        session.flush.assert_called_once()

    async def test_update_ignores_sa_state(self) -> None:
        """Проверка что _sa_instance_state всегда игнорируется.

        Данный тест проверяет, что системное поле _sa_instance_state
        всегда игнорируется при обновлении модели.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)
        existing_model = TestModel(id_=1, name='old_name')
        new_data = TestModel(id_=0, name='new_name')
        setattr(new_data, '_sa_instance_state', 'should_be_ignored')

        result = await repo._update(
            existing_model=existing_model,
            new_data=new_data,
        )

        assert_that(
            actual_or_assertion=result.name,
            matcher=equal_to(obj=new_data.name),
        )
        state = getattr(result, '_sa_instance_state', None)
        assert_that(
            actual_or_assertion=state is not None,
            matcher=equal_to(obj=True),
        )
        # Проверяем, что метод flush был вызван
        session.flush.assert_called_once()

    async def test_execute(self) -> None:
        """Проверка метода execute.

        Данный тест проверяет вызов метода execute у сессии
        для выполнения SQL запросов.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        from sqlalchemy import text

        statement = text('SELECT 1')
        await repo.execute(
            statement=statement,
            is_use_active_transaction=True,
        )

        # Проверяем, что метод execute был вызван с правильным аргументом
        session.execute.assert_called_once_with(statement)

    async def test_refresh(self, test_model: TestModel) -> None:
        """Проверка метода refresh.

        Данный тест проверяет вызов метода refresh у сессии
        для обновления экземпляра модели из базы данных.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        await repo.refresh(instance=test_model)

        # Проверяем, что метод refresh был вызван с правильным аргументом
        session.refresh.assert_called_once_with(test_model)

    # Тесты для обработки ошибок и rollback
    async def test_rollback_on_error_in_add_record(
        self,
        test_model: TestModel,
    ) -> None:
        """Проверка rollback при ошибке в _add_record.

        Данный тест проверяет, что при возникновении ошибки
        в методе _add_record происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        with patch.object(
            target=session,
            attribute='flush',
            side_effect=Exception('Database error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Database error',
            ):
                await repo._add_record(model=test_model)

            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    async def test_rollback_on_error_in_update(self) -> None:
        """Проверка rollback при ошибке в _update.

        Данный тест проверяет, что при возникновении ошибки
        в методе _update происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)
        existing_model = TestModel(id_=1, name='old_name')
        new_data = TestModel(id_=1, name='new_name')

        with patch.object(
            target=session,
            attribute='flush',
            side_effect=Exception('Database error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Database error',
            ):
                await repo._update(
                    existing_model=existing_model,
                    new_data=new_data,
                )

            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    async def test_rollback_on_error_in_commit(self) -> None:
        """Проверка rollback при ошибке в commit.

        Данный тест проверяет, что при возникновении ошибки
        в методе commit происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        with patch.object(
            target=session,
            attribute='commit',
            side_effect=Exception('Commit error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Commit error',
            ):
                await repo.commit()

            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    async def test_rollback_on_error_in_flush(self) -> None:
        """Проверка rollback при ошибке в flush.

        Данный тест проверяет, что при возникновении ошибки
        в методе flush происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        with patch.object(
            target=session,
            attribute='flush',
            side_effect=Exception('Flush error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Flush error',
            ):
                await repo.flush()

            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    async def test_rollback_on_error_in_execute(self) -> None:
        """Проверка rollback при ошибке в execute.

        Данный тест проверяет, что при возникновении ошибки
        в методе execute происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        from sqlalchemy import text

        statement = text('SELECT 1')

        with patch.object(
            target=session,
            attribute='execute',
            side_effect=Exception('Execute error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Execute error',
            ):
                await repo.execute(
                    statement=statement,
                    is_use_active_transaction=True,
                )
            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    async def test_rollback_on_error_in_refresh(
        self,
        test_model: TestModel,
    ) -> None:
        """Проверка rollback при ошибке в refresh.

        Данный тест проверяет, что при возникновении ошибки
        в методе refresh происходит откат транзакции.
        """
        session = AsyncMock()
        repo = TestRepository(session=session)

        with patch.object(
            target=session,
            attribute='refresh',
            side_effect=Exception('Refresh error'),
        ):
            with pytest.raises(
                expected_exception=Exception,
                match='Refresh error',
            ):
                await repo.refresh(instance=test_model)

            # Проверяем, что rollback был вызван
            assert_that(
                actual_or_assertion=session.rollback.call_count,
                matcher=greater_than_or_equal_to(1),
            )

    @patch.object(
        target=SampleRepo,
        attribute='execute',
        new_callable=AsyncMock,
    )
    async def test_is_connection_exist_success(
        self,
        repo_execute_mock: AsyncMock,
    ) -> None:
        """Проверка метода _is_connection_exist_success.

        Данный тест проверяет возвращается ли
        значение "True" при успешном execute в сессии.
        """
        repo_execute_mock.return_value = None
        repo = SampleRepo(session=AsyncMock())

        result = await repo._is_connection_exist()

        assert_that(
            actual_or_assertion=result,
            matcher=is_(True),
        )

    @patch.object(
        target=SampleRepo,
        attribute='execute',
        new_callable=AsyncMock,
    )
    async def test_is_connection_exist_failed(
        self,
        repo_execute_mock: AsyncMock,
    ) -> None:
        """Проверка метода _is_connection_exist_success.

        Данный тест проверяет возвращается ли
        значение "False" при неудачном execute в сессии.
        """
        repo_execute_mock.side_effect = InterfaceError(
            statement='SELECT 1',
            params={},
            orig=Exception('Соединение отсутствует'),
            connection_invalidated=True,
        )
        repo = SampleRepo(session=AsyncMock())

        result = await repo._is_connection_exist()

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
