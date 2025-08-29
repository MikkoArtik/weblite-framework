"""Модуль логирования для weblite-framework."""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

__all__ = [
    'JsonFormatter',
    'get_logger',
]


class JsonFormatter(logging.Formatter):
    """Форматируем лог-сообщения в JSON формате с полями.

    Поля:
        timestamp: Временная метка.
        level: Уровень логирования.
        source: Источник сообщения (модуль).
        message: Текст сообщения.
    """

    def format(self: 'JsonFormatter', record: logging.LogRecord) -> str:
        """Форматируем запись лога в JSON строку.

        Args:
            record(logging.LogRecord): Запись лога для форматирования.

        Returns:
              str: JSON-строка с отформатированным логом.
        """
        log_record = {
            'timestamp': datetime.fromtimestamp(record.created)
            .astimezone()
            .isoformat(),
            'level': record.levelname,
            'source': record.module,
            'message': record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)


_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Создаем и возвращаем логгер.

    Логирование происходит в отдельном потоке через QueueHandler.

    Args:
        name (str): Имя логгера.

    Returns:
        logging.Logger: Настроенный логгер.
    """
    if name in _loggers:
        return _loggers[name]

    logger: logging.Logger = logging.getLogger(name=name)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(get_handler())

    _loggers[name] = logger

    return logger


_handler: logging.Handler | None = None


def get_handler() -> logging.Handler:
    """Создаем общую очередь с listener для всех loggers."""
    global _handler

    if _handler is not None:
        return _handler

    log_queue: Queue[logging.LogRecord] = Queue()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())

    listener = QueueListener(log_queue, stream_handler)
    listener.start()

    _handler = QueueHandler(log_queue)

    return _handler
