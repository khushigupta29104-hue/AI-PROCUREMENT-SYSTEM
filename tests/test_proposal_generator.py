"""
Tests the config-consistency of field_mapping.json / proposal_config.json
(pure logic, no Ollama API or ChromaDB required).
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.config_loader import get_field_mapping, get_proposal_config  # noqa: E402


def test_every_proposal_type_has_a_matching_field_mapping_entry():
    proposal_ids = {t["id"] for t in get_proposal_config()["proposal_types"]}
    field_mapping_ids = set(get_field_mapping()["proposal_types"].keys())
    assert proposal_ids == field_mapping_ids


def test_every_field_has_a_valid_source_type():
    mapping = get_field_mapping()
    valid_sources = set(mapping["source_types"].keys())
    for type_id, type_cfg in mapping["proposal_types"].items():
        for field in type_cfg["fields"]:
            assert field["source"] in valid_sources, (
                f"Field '{field['field_name']}' in '{type_id}' has invalid source '{field['source']}'"
            )


def test_every_proposal_type_has_header_fields_metadata():
    for t in get_proposal_config()["proposal_types"]:
        assert "header_fields" in t
        for key in ("reference_no", "customer_vendor", "reference"):
            assert key in t["header_fields"]
