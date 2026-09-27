"""Tests services/analytics_service.py's pure-filesystem computations (no Ollama/ChromaDB required)."""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from services.analytics_service import get_document_category_distribution, get_storage_utilization  # noqa: E402


def test_document_category_distribution_covers_all_configured_categories():
    from utils.config_loader import get_system_config
    categories = get_system_config()["knowledge_base_categories"]
    labels = get_system_config()["knowledge_base_category_labels"]
    dist = get_document_category_distribution()
    returned_labels = {d["category"] for d in dist}
    expected_labels = {labels[c] for c in categories}
    assert returned_labels == expected_labels


def test_storage_utilization_returns_four_folders():
    storage = get_storage_utilization()
    assert set(storage.keys()) == {"Uploads", "Knowledge Base", "Generated Proposals", "Vector Database"}
    assert all(isinstance(v, float) for v in storage.values())
