#!/usr/bin/env python3
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path
from collections import defaultdict

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import HitterMetricDaily, Player, Salary, Slate, StackScoreDaily
from scripts.common import log_run


def main(run_date: date | None = None, site: str = "dk"):
    d = run_date or date.today()
    db = SessionLocal()
    try:
        slate = db.execute(select(Slate).where(Slate.slate_date == d, Slate.site == site, Slate.contest_type == "main")).scalar_one_or_none()
        if not slate:
            raise RuntimeError("No slate found")
        db.query(StackScoreDaily).filter(StackScoreDaily.score_date == d, StackScoreDaily.site == site).delete()
        q = (
            select(HitterMetricDaily, Player, Salary)
            .join(Player, Player.id == HitterMetricDaily.player_id)
            .join(Salary, (Salary.player_id == Player.id) & (Salary.slate_id == slate.id), isouter=True)
            .where(HitterMetricDaily.metric_date == d)
        )
        grouped = defaultdict(list)
        for m, p, s in db.execute(q).all():
            grouped[p.team_id].append((m, s.salary if s else 3500))

        for team_id, hitters in grouped.items():
            hitters = sorted(hitters, key=lambda x: x[0].projection, reverse=True)
            top5 = hitters[:5]
            if not top5:
                continue
            proj = sum(h[0].projection for h in top5)
            ceil = sum(h[0].ceiling for h in top5)
            salary = int(sum(h[1] for h in top5))
            own = round(min(35.0, max(3.0, proj * 0.75)), 2)
            lev = round((ceil - proj) / max(1, own), 3)
            db.add(StackScoreDaily(
                score_date=d,
                site=site,
                team_id=team_id,
                stack_score=round(proj, 3),
                ceiling_score=round(ceil, 3),
                value_score=round(proj / (salary / 1000), 3),
                ownership_proxy=own,
                leverage_score=lev,
                top5_projection=round(proj, 3),
                salary_estimate=salary,
                mini_stack_score=round(proj * 0.62, 3),
                one_off_score=round(max(h[0].ceiling for h in hitters), 3),
            ))
        db.commit()
        log_run(db, "compute_stack_scores", "success", f"teams={len(grouped)}")
    except Exception as exc:
        db.rollback()
        log_run(db, "compute_stack_scores", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
