from functools import wraps
from typing import Callable, Any, TypeVar
import sys

from loguru import logger

from rezehor.utils.config import get_config

T = TypeVar("T", bound=Callable[..., Any])


def setup_logger() -> None:
    """Initialize logging system."""
    config = get_config()

    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.logging.level,
        colorize=True,
    )

    log_path = config.settings.data_dir / "logs" / "rezehor.log"
    logger.add(
        log_path,
        rotation=config.logging.rotation,
        retention=config.logging.retention,
        level=config.logging.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True,
    )

    logger.info("Logger initialized")


def log_execution(func: T) -> T:
    """Decorator to log function execution."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(
            f"Executing {func.__name__} with args={args}, kwargs={kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise

    return wrapper


__all__ = ["logger", "setup_logger", "log_execution"]
