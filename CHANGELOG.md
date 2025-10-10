## _Changelog_

Формата файла: [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

Версионирование: [Semantic Versioning](https://semver.org/lang/ru/).

Блоки изменений:

|   Название   | Когда применить                                                        |
|:------------:|------------------------------------------------------------------------|
|  Добавлено   | Появился новый функционал.                                             |
|   Изменено   | Изменен существующий функционал.                                       |
|   Устарело   | Выделен функционал, который будет удален в одном из следующих релизов. |
|   Удалено    | Удален существующий функционал.                                        |
|  Исправлено  | Исправлен баг.                                                         |
| Безопасность | Выявлена уязвимость.                                                   |

## [Unreleased]

### Добавлено
- Модули исключений `auth`, `repository`;
- Зависимость fastapi в `pyproject.toml`

## [0.3.0]

### Добавлено
- Модуль кастомных валидаторов `weblite_framework/schemas/validators.py`; 
- Тесты кастомных валидаторов `tests/schemas/test_validators.py`;
- Библиотека freezegun в раздел `tool.poetry.group.test.dependencies`;

## [0.2.0]

### Добавлено
- Сервисный слой для проверки работоспособности сервиса (`HealthService`) в пакет `weblite_framework/service/health.py`;
- Юнит-тесты для `HealthService` с проверкой различных сценариев работоспособности;
- Исключения `ServiceHealthError` и `DatabaseConnectionError` для обработки ошибок соединения;
- Класс `CommonRepo` для проверки соединения с базой данных;
- Метод `_is_connection_exist` в `BaseRepositoryClass` для проверки соединения с базой данных;
- Юнит-тесты для метода `_is_connection_exist` (успешное соединение и ошибка `InterfaceError`);
- Вспомогательные классы для тестов репозитория (`SampleModel`, `SampleDTO`, `SampleRepo`);

### Изменено
- Переименован `_get_session_for_testing` в `session` (теперь это публичное свойство)
- Тест `test_initialization` в `test_base.py` обновлён на использование свойства `session`.

## [0.1.0]

### Добавлено

- Класс логирования;
- Базовый класс `BaseRepositoryClass` для создания репозиториев;
- Абстрактные методы `_model_to_dto` и `_dto_to_model` для маппинга данных;
- Методы для работы с БД: `_add_record`, `_update`, `add`, `commit`, `execute`, `refresh`, `flush`;
- Обработка ошибок с автоматическим rollback для всех транзакций;
- Поддержка игнорирования полей при обновлении (`ignore_fields`);
- Автоматическое игнорирование `_sa_instance_state` при обновлении;
- Тесты для базового репозитория, включая тесты обработки ошибок и rollback;
- Полное покрытие тестами всех методов базового класса;
- Документация по использованию BaseRepositoryClass в README.md;
- Родительская модель `CustomBaseModel` (на основе Pydantic v2) в `weblite_framework/schemas/base.py`;
- Тесты для `CustomBaseModel` в `weblite_framework/tests/models/test_model.py`;
- Документация в README.md по использованию и требованиям;
- Реализован провайдер `S3Provider` для работы с S3 (методы загрузки, получения, удаления и листинга файлов);
- Написаны юнит-тесты для `S3Provider` с использованием pytest и pytest-asyncio, включая мокирование aioboto3 и асинхронную пагинацию;
- Конфигурация линтеров flake8, black, isort и mypy в pyproject.toml;
- flake8 настроен с inline-quotes = "'", max-line-length = 79, docstring-convention = "google", require-annotations = true, max-complexity = 5, игнорированием ошибки ANN101,D104;
- black с длиной строки 79 и отключённой нормализацией кавычек;
- isort с трейлинговыми запятыми, многолинейным выводом и длиной строки 79;
- mypy с строгой проверкой, поддержкой плагина pydantic;
- Базовые файлы проекта;

