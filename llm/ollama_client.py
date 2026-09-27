"""
ollama_client.py
=================
Thin wrapper around LangChain's ChatOllama class. Ollama runs open-
weight models (Llama 3.1, etc.) entirely on your own machine -- no API
key, no internet dependency, no usage quota, and no risk of a provider
retiring a model overnight.

All prompt construction stays OUTSIDE this file (see prompts/ and
llm/prompt_runner.py) -- this module only knows how to talk to the
local Ollama server.

Requires Ollama to be installed and running (`ollama serve`), with the
configured model already pulled (e.g. `ollama pull llama3.1:8b`).
"""

from functools import lru_cache

import requests
from langchain_ollama import ChatOllama

from llm.llm_config import get_llm_settings
from utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    """Returns a cached ChatOllama instance configured from system_config.json."""
    cfg = get_llm_settings()
    logger.info("Initializing ChatOllama model='%s' host='%s'", cfg["llm_model"], cfg["host"])
    return ChatOllama(
        model=cfg["llm_model"],
        base_url=cfg["host"],
        temperature=cfg["temperature"],
        num_predict=cfg["max_output_tokens"],
    )


def generate(prompt: str) -> str:
    """
    Sends `prompt` to the local Ollama server and returns the plain
    text response.

    Raises:
        RuntimeError: if Ollama is unreachable or the configured model
            has not been pulled yet.
    """
    llm = get_llm()
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:  # noqa: BLE001
        logger.error("Ollama generation failed: %s", exc)
        raise RuntimeError(
            "Could not reach the local Ollama server. Please ensure Ollama is running "
            "('ollama serve') and the configured model has been pulled "
            "('ollama pull <model_name>')."
        ) from exc


def health_check() -> bool:
    """
    Pings the Ollama HTTP API's /api/tags endpoint to check the server
    is reachable. Used by the sidebar's connection-status indicator.
    """
    cfg = get_llm_settings()
    try:
        resp = requests.get(f"{cfg['host']}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:  # noqa: BLE001
        return False
