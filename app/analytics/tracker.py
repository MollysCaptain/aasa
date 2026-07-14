"""
Card 3.3 — Lightweight local event log. Appends one JSON line per event to
data/telemetry.log — "trend only" metrics, per the Handbook's metric list,
not a dashboard-grade analytics pipeline.
"""
import json
import time
from pathlib import Path

LOG_PATH = Path("data/telemetry.log")
LOG_PATH.parent.mkdir(exist_ok=True)


def log_event(event_name: str, **fields):
    """
    event_name examples used across this project:
      "form_start", "field_changed", "form_submit", "results_shown",
      "export_clicked", "survey_submitted"
    """
    entry = {"event": event_name, "timestamp": time.time(), **fields}
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
