#!/usr/bin/env python3
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path

from pybaseball import batting_stats
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import Team, TeamMetricDaily
from scripts.common import log_run


def main(run_date: date | None = None):
    d = run_date or date.today()
    db = SessionLocal()
    try:
        df = batting_stats(d.year, qual=20)
        db.query(TeamMetricDaily).filter(TeamMetricDaily.metric_date == d).delete()
        by_team = df.groupby("Team").agg({"wOBA": "mean", "ISO": "mean", "K%": "mean", "BB%": "mean", "HardHit%": "mean", "Barrel%": "mean", "R": "sum", "G": "sum"}).reset_index()
        for _, r in by_team.iterrows():
            t = db.execute(select(Team).where(Team.code == r["Team"])).scalar_one_or_none()
            if not t:
                continue
            db.add(TeamMetricDaily(metric_date=d, team_id=t.id, woba=float(r["wOBA"]), iso=float(r["ISO"]), k_pct=float(r["K%"]), bb_pct=float(r["BB%"]), hard_hit_pct=float(r["HardHit%"]), barrel_pct=float(r["Barrel%"]), runs_per_game_14=float(r["R"]/max(1,r["G"])), bullpen_weakness=5.0))
        db.commit()
        log_run(db, "compute_team_metrics", "success", f"teams={len(by_team)}")
    except Exception as exc:
        db.rollback()
        log_run(db, "compute_team_metrics", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
