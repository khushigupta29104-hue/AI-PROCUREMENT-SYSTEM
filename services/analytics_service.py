"""
analytics_service.py
======================
Computes the datasets shown on the Analytics dashboard page: document
category distribution, proposal-type distribution, monthly upload
trend, knowledge-base growth over time, and storage utilization.
All figures are derived purely from filesystem metadata (file counts
and modification timestamps) - no separate analytics database needed.
"""

import os
from collections import Counter
from datetime import datetime
from typing import Dict, List

from utils.config_loader import get_proposal_config, get_system_config, resolve_path
from utils.file_utils import get_file_metadata, get_folder_size_mb, list_files


def get_document_category_distribution() -> List[Dict]:
    """Returns [{"category": "SPR", "count": 5}, ...] for the knowledge base pie/bar chart."""
    cfg = get_system_config()
    labels = cfg["knowledge_base_category_labels"]
    results = []
    for cat in cfg["knowledge_base_categories"]:
        folder = resolve_path("knowledge_base", cat)
        count = len(list_files(folder, extensions=[".pdf", ".docx"]))
        results.append({"category": labels.get(cat, cat), "count": count})
    return results


def get_proposal_type_distribution() -> List[Dict]:
    """Returns [{"type": "Honeywell", "count": 3}, ...] from generated_proposals/docx/ filenames."""
    docx_dir = resolve_path(get_system_config()["proposal_output"]["docx_output_dir"])
    type_labels = {t["id"]: t["display_name"] for t in get_proposal_config()["proposal_types"]}

    counter = Counter()
    for path in list_files(docx_dir, extensions=[".docx"]):
        base_name = os.path.splitext(os.path.basename(path))[0]
        type_id = base_name.split("_")[0]
        counter[type_labels.get(type_id, type_id)] += 1

    return [{"type": k, "count": v} for k, v in counter.items()]


def get_monthly_upload_trend() -> List[Dict]:
    """Returns [{"month": "2026-07", "uploads": 4}, ...] across all knowledge-base categories, sorted chronologically."""
    cfg = get_system_config()
    counter = Counter()
    for cat in cfg["knowledge_base_categories"]:
        folder = resolve_path("knowledge_base", cat)
        for path in list_files(folder, extensions=[".pdf", ".docx"]):
            month = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m")
            counter[month] += 1
    return [{"month": k, "uploads": v} for k, v in sorted(counter.items())]


def get_knowledge_base_growth() -> List[Dict]:
    """Returns a cumulative document-count-over-time series for the KB growth line chart."""
    trend = get_monthly_upload_trend()
    cumulative = 0
    growth = []
    for point in trend:
        cumulative += point["uploads"]
        growth.append({"month": point["month"], "total_documents": cumulative})
    return growth


def get_recent_activity_timeline(limit: int = 15) -> List[Dict]:
    """Returns the most recently modified files across knowledge_base/ and generated_proposals/, newest first."""
    cfg = get_system_config()
    entries = []

    for cat in cfg["knowledge_base_categories"]:
        folder = resolve_path("knowledge_base", cat)
        for path in list_files(folder, extensions=[".pdf", ".docx"]):
            meta = get_file_metadata(path)
            entries.append({"event": "Document Uploaded", "detail": meta["filename"], "timestamp": meta["modified"]})

    docx_dir = resolve_path(cfg["proposal_output"]["docx_output_dir"])
    for path in list_files(docx_dir, extensions=[".docx"]):
        meta = get_file_metadata(path)
        entries.append({"event": "Proposal Generated", "detail": meta["filename"], "timestamp": meta["modified"]})

    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries[:limit]


def get_storage_utilization() -> Dict:
    """Returns storage breakdown (MB) across uploads/, knowledge_base/, generated_proposals/, vector_db/."""
    return {
        "Uploads": get_folder_size_mb(resolve_path("uploads")),
        "Knowledge Base": get_folder_size_mb(resolve_path("knowledge_base")),
        "Generated Proposals": get_folder_size_mb(resolve_path("generated_proposals")),
        "Vector Database": get_folder_size_mb(resolve_path("vector_db")),
    }


def get_todays_upload_count() -> int:
    """Counts documents uploaded today (by file modification date) - used on the Dashboard's 'Today's Uploads' metric."""
    cfg = get_system_config()
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0
    for cat in cfg["knowledge_base_categories"]:
        folder = resolve_path("knowledge_base", cat)
        for path in list_files(folder, extensions=[".pdf", ".docx"]):
            if get_file_metadata(path)["modified_date"] == today:
                count += 1
    return count
