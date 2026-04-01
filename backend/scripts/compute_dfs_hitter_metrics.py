#!/usr/bin/env python3
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import HitterMetricDaily, Salary, Slate
from scripts.common import log_run


def main(run_date: date | None = None, site: str = "dk"):
    d = run_date or date.today()
    db = SessionLocal()
    try:
        slate = db.execute(select(Slate).where(Slate.slate_date == d, Slate.site == site, Slate.contest_type == "main")).scalar_one_or_none()
        if not slate:
            raise RuntimeError("No slate found for date/site")
        q = select(HitterMetricDaily, Salary).join(Salary, (Salary.player_id == HitterMetricDaily.player_id) & (Salary.slate_id == slate.id), isouter=True).where(HitterMetricDaily.metric_date == d)
        for metric, salary in db.execute(q).all():
            salary_value = salary.salary if salary else 4000
            metric.value_score = round(metric.projection / (salary_value / 1000), 3)
            metric.leverage_score = round(metric.ceiling / max(1, salary_value / 1000), 3)
        db.commit()
        log_run(db, "compute_dfs_hitter_metrics", "success", "updated hitter value scores")
    except Exception as exc:
        db.rollback()
        log_run(db, "compute_dfs_hitter_metrics", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
