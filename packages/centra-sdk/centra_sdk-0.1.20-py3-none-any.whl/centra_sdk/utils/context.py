import logging
import sys
import os
import httpx
import threading
from typing import Optional
from dataclasses import dataclass, field
from functools import wraps


def thread_safe_singleton(func):
    """Decorator to make singleton initialization thread-safe."""
    lock = threading.Lock()

    @wraps(func)
    def wrapper(cls):
        if not cls.CONTEXT:
            with lock:
                if not cls.CONTEXT:  # double-check pattern
                    return func(cls)
        return cls.CONTEXT
    return wrapper


@dataclass
class IntegrationContext:
    httpx_client: httpx.AsyncClient = field(default_factory=httpx.AsyncClient)
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger('centra_sdk'))


class IntegrationContextApi:
    CONTEXT: Optional[IntegrationContext] = None

    @classmethod
    def _get_log_level(cls) -> int:
        """Get log level from environment variable or default to INFO."""
        level_name = os.getenv('CENTRA_SDK_LOG_LEVEL', 'INFO').upper()
        return getattr(logging, level_name, logging.INFO)

    @classmethod
    async def clean(cls):
        if cls.CONTEXT:
            await cls.CONTEXT.httpx_client.aclose()

    @classmethod
    @thread_safe_singleton
    def context(cls):
        if cls.CONTEXT is None:
            cls.CONTEXT = IntegrationContext()
            if not cls.CONTEXT.logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
                handler.setFormatter(formatter)
                cls.CONTEXT.logger.addHandler(handler)

            cls.CONTEXT.logger.setLevel(cls._get_log_level())

        return cls.CONTEXT

    @classmethod
    def client(cls):
        return cls.context().httpx_client

    @classmethod
    def log(cls):
        return cls.context().logger

    @classmethod
    def set_log_level(cls, level: int):
        """Set the log level for the SDK logger."""
        if cls.CONTEXT:
            cls.CONTEXT.logger.setLevel(level)
