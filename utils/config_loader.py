"""
config_loader.py
=================
Loads and caches the three JSON configuration files (system_config.json,
proposal_config.json, field_mapping.json) from config/. Centralizing
this avoids re-implementing path/JSON logic everywhere, and gives us
one place to clear the cache after the Settings page saves changes.
"""

import json
import os
from functools import lru_cache

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_DIR = os.path.join(_PROJECT_ROOT, "config")


def get_project_root() -> str:
    return _PROJECT_ROOT


def _load_json(filename: str) -> dict:
    path = os.path.join(_CONFIG_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_system_config() -> dict:
    return _load_json("system_config.json")


@lru_cache(maxsize=1)
def get_proposal_config() -> dict:
    return _load_json("proposal_config.json")


@lru_cache(maxsize=1)
def get_field_mapping() -> dict:
    return _load_json("field_mapping.json")


def resolve_path(*relative_parts: str) -> str:
    return os.path.join(_PROJECT_ROOT, *relative_parts)


def clear_config_cache() -> None:
    get_system_config.cache_clear()
    get_proposal_config.cache_clear()
    get_field_mapping.cache_clear()
