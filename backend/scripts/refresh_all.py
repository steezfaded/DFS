#!/usr/bin/env python3
from __future__ import annotations

import subprocess


SCRIPTS = [
    "backend/scripts/ingest_mlb_schedule.py",
    "backend/scripts/ingest_statcast.py",
    "backend/scripts/compute_dfs_hitter_metrics.py",
    "backend/scripts/compute_dfs_pitcher_metrics.py",
    "backend/scripts/compute_team_metrics.py",
    "backend/scripts/compute_stack_scores.py",
]


def main():
    for script in SCRIPTS:
        print(f"Running {script}")
        subprocess.check_call(["python", script])


if __name__ == "__main__":
    main()
