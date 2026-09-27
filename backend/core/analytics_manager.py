"""
analytics_manager.py
======================
Thin facade over services/analytics_service.py, called by the
Analytics dashboard page and by the Dashboard/Home page's summary
metrics (Today's Uploads, Storage Used).
"""

from typing import Dict, List

from services.analytics_service import (
    get_document_category_distribution,
    get_knowledge_base_growth,
    get_monthly_upload_trend,
    get_proposal_type_distribution,
    get_recent_activity_timeline,
    get_storage_utilization,
    get_todays_upload_count,
)


def get_full_analytics_snapshot() -> Dict:
    """Returns every dataset the Analytics page's charts need, computed in one call."""
    return {
        "category_distribution": get_document_category_distribution(),
        "proposal_type_distribution": get_proposal_type_distribution(),
        "monthly_upload_trend": get_monthly_upload_trend(),
        "kb_growth": get_knowledge_base_growth(),
        "recent_activity": get_recent_activity_timeline(),
        "storage_utilization": get_storage_utilization(),
    }


def get_todays_uploads() -> int:
    return get_todays_upload_count()


def get_total_storage_mb() -> float:
    storage = get_storage_utilization()
    return round(sum(storage.values()), 2)
