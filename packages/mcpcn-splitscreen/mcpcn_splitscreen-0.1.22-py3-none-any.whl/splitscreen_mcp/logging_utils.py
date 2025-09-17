import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


_LOGGER: Optional[logging.Logger] = None


def _ensure_log_dir() -> str:
    """Ensure the base log directory exists and return the log file path.

    Path: ~/.mcp/splitscreen-mcp/splitscreen.log
    """
    home = os.path.expanduser("~")
    base_dir = os.path.join(home, ".mcp", "splitscreen-mcp")
    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception:
        # If directory creation fails, fallback to current working directory
        base_dir = os.getcwd()
    return os.path.join(base_dir, "splitscreen.log")


def get_logger() -> logging.Logger:
    """Get a module-level singleton logger configured for rotating file logs."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger("splitscreen_mcp")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_path = _ensure_log_dir()
    handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,  # ~1MB per file
        backupCount=3,
        encoding="utf-8",
    )
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(process)d:%(threadName)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)

    # Avoid duplicate handlers on reload
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(handler)

    _LOGGER = logger
    return logger


def log_startup(component: str) -> None:
    try:
        get_logger().info(f"Startup: {component}")
    except Exception:
        pass


def log_exception(msg: str) -> None:
    try:
        get_logger().exception(msg)
    except Exception:
        pass


