#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
from pybaseball import batting_stats, pitching_stats
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import HitterMetricDaily, PitcherMetricDaily, Player, Team
from scripts.common import log_run


def upsert_player(db, name: str, team_code: str | None, is_pitcher: bool) -> Player:
    p = db.execute(select(Player).where(Player.name == name)).scalar_one_or_none()
    team_id = None
    if team_code:
        t = db.execute(select(Team).where(Team.code == team_code)).scalar_one_or_none()
        team_id = t.id if t else None
    if not p:
        p = Player(name=name, team_id=team_id, is_pitcher=is_pitcher)
        db.add(p)
        db.flush()
    return p


def main(run_date: date | None = None):
    d = run_date or date.today()
    year = d.year
    db = SessionLocal()
    try:
        hitters = batting_stats(year, qual=10)
        pitchers = pitching_stats(year, qual=10)

        db.query(HitterMetricDaily).filter(HitterMetricDaily.metric_date == d).delete()
        db.query(PitcherMetricDaily).filter(PitcherMetricDaily.metric_date == d).delete()

        for _, r in hitters.head(500).iterrows():
            p = upsert_player(db, r["Name"], r.get("Team"), False)
            proj = max(0.0, r.get("wRC+", 100) / 10 + r.get("HR", 0) * 0.15 + r.get("SB", 0) * 0.12)
            db.add(HitterMetricDaily(
                metric_date=d,
                player_id=p.id,
                pa_proj=float(r.get("PA", 0)) / max(1, r.get("G", 1)),
                woba=float(r.get("wOBA", 0)),
                xwoba=float(r.get("xwOBA", r.get("wOBA", 0))),
                iso=float(r.get("ISO", 0)),
                barrel_pct=float(r.get("Barrel%", 0)),
                hard_hit_pct=float(r.get("HardHit%", 0)),
                k_pct=float(r.get("K%", 0)),
                bb_pct=float(r.get("BB%", 0)),
                recent_form=float(r.get("wRC+", 100)) / 100,
                projection=proj,
                floor=max(1.0, proj * 0.55),
                ceiling=proj * 1.55,
                value_score=proj,
                leverage_score=float(np.clip((r.get("ISO", 0.1) * 4) - (r.get("K%", 0.2) * 2), 0, 10)),
            ))

        for _, r in pitchers.head(250).iterrows():
            p = upsert_player(db, r["Name"], r.get("Team"), True)
            kbb = float(r.get("K-BB%", 0))
            proj = max(0.0, (kbb * 0.9) + float(r.get("IP", 0)) * 0.07)
            db.add(PitcherMetricDaily(
                metric_date=d,
                player_id=p.id,
                ip_proj=float(r.get("IP", 0)) / max(1, r.get("GS", 1)),
                k_pct=float(r.get("K%", 0)),
                bb_pct=float(r.get("BB%", 0)),
                k_minus_bb=kbb,
                xera=float(r.get("ERA", 4.2)),
                xwoba_allowed=float(r.get("AVG", 0.24)),
                hard_hit_allowed=float(r.get("HardHit%", 0)),
                swstr_pct=float(r.get("SwStr%", 0)),
                csw_pct=float(r.get("CSW%", 0)),
                projection=proj,
                floor=max(3.0, proj * 0.65),
                ceiling=proj * 1.45,
                value_score=proj,
                leverage_score=float(np.clip(kbb / 3, 0, 10)),
                cash_safety=float(np.clip(10 - float(r.get("BB%", 8)) / 2, 1, 10)),
                gpp_upside=float(np.clip(kbb / 2 + float(r.get("SwStr%", 10)) / 3, 1, 10)),
            ))

        db.commit()
        log_run(db, "ingest_statcast", "success", f"loaded hitters={len(hitters)} pitchers={len(pitchers)}")
    except Exception as exc:
        db.rollback()
        log_run(db, "ingest_statcast", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
