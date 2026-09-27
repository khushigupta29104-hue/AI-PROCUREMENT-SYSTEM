"""
logger.py
=========
Centralized logging setup. Every module obtains its logger like:

    from utils.logger import get_logger
    logger = get_logger(__name__)

All log lines land in logs/app.log (rotating) so uploads, retrieval,
knowledge-base updates, proposal generation, downloads, warnings, and
errors are all auditable after the fact.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from utils.config_loader import get_system_config

_LOGGING_CONFIGURED = False


def _configure_root_logger() -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    cfg = get_system_config().get("logging", {})
    log_dir = cfg.get("log_dir", "logs")
    log_file = cfg.get("log_file", "app.log")
    level_name = cfg.get("level", "INFO")
    max_bytes = int(cfg.get("max_bytes", 5 * 1024 * 1024))
    backup_count = int(cfg.get("backup_count", 5))

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))

    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
               for h in root_logger.handlers):
        root_logger.addHandler(console_handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(name)
