import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from datetime import datetime
import sys
import json


class JsonFormatter(logging.Formatter):
    """Форматируем лог-сообщения в JSON формате с полями:

    timestamp, level, source, message
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).astimezone().isoformat(),
            "level": record.levelname,
            "source": record.module,
            "message": record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)

_loggers: dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """Создаем и возвращаем logger с именем 'name'

    Логирование происходит в отдельном потоке через QueueHandler
    """

    if name in _loggers:
        return _loggers[name]

    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_handler())

    _loggers[name] = logger

    return logger

_handler: logging.Handler | None = None

def get_handler() -> logging.Handler:
    """Создаем общую очередь с listener для всех логеров
    """

    global _handler

    if _handler is not None:
        return _handler

    log_queue = Queue()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())

    listener = QueueListener(log_queue, stream_handler)
    listener.start()

    _handler = QueueHandler(log_queue)

    return _handler
