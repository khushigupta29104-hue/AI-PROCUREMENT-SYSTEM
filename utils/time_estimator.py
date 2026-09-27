"""
time_estimator.py
==================
Tracks per-stage timing during proposal generation to compute
"Estimated Remaining Time" and "Elapsed Time" for the live progress UI.
"""

import time
from typing import Dict, List

DEFAULT_STAGE_DURATIONS: Dict[str, float] = {
    "reading_documents": 1.0,
    "searching_knowledge_base": 1.5,
    "retrieving_spr": 2.0,
    "retrieving_registration": 2.0,
    "retrieving_purchase_order": 2.0,
    "retrieving_tender": 2.0,
    "retrieving_vendor": 2.0,
    "generating_proposal": 3.0,
    "exporting_docx": 1.0,
    "exporting_pdf": 1.5,
}


class TimeEstimator:
    """Tracks stage start times for one generation run and computes elapsed/remaining time."""

    def __init__(self, stage_order: List[str]):
        self.stage_order = stage_order
        self.start_time = time.time()
        self.stage_start_times: Dict[str, float] = {}
        self.stage_durations: Dict[str, float] = {}

    def start_stage(self, stage_key: str) -> None:
        self.stage_start_times[stage_key] = time.time()

    def end_stage(self, stage_key: str) -> None:
        started = self.stage_start_times.get(stage_key, time.time())
        self.stage_durations[stage_key] = time.time() - started

    def estimated_remaining_seconds(self, current_stage_index: int) -> float:
        remaining_stages = self.stage_order[current_stage_index + 1:]
        return sum(DEFAULT_STAGE_DURATIONS.get(s, 1.5) for s in remaining_stages)

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    @staticmethod
    def format_seconds(seconds: float) -> str:
        seconds = max(0, int(round(seconds)))
        if seconds < 60:
            return f"{seconds}s"
        minutes, secs = divmod(seconds, 60)
        return f"{minutes}m {secs}s"
