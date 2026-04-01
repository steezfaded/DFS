#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import requests
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import Game, Slate, Team
from scripts.common import log_run


def get_or_create_team(db, code: str) -> Team:
    t = db.execute(select(Team).where(Team.code == code)).scalar_one_or_none()
    if not t:
        t = Team(code=code, name=code, park=None, park_factor=1.0)
        db.add(t)
        db.flush()
    return t


def main(run_date: date | None = None):
    d = run_date or date.today()
    db = SessionLocal()
    try:
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={d.isoformat()}"
        payload = requests.get(url, timeout=30).json()
        dates = payload.get("dates", [])
        games = dates[0].get("games", []) if dates else []

        db.query(Game).filter(Game.game_date == d).delete()
        for g in games:
            away_code = g["teams"]["away"]["team"]["abbreviation"]
            home_code = g["teams"]["home"]["team"]["abbreviation"]
            away = get_or_create_team(db, away_code)
            home = get_or_create_team(db, home_code)
            db.add(Game(game_date=d, away_team_id=away.id, home_team_id=home.id, run_env_score=0.0))

        for site in ["dk", "fd"]:
            slate = db.execute(select(Slate).where(Slate.slate_date == d, Slate.site == site, Slate.contest_type == "main")).scalar_one_or_none()
            if not slate:
                db.add(Slate(slate_date=d, site=site, contest_type="main", game_count=len(games)))
            else:
                slate.game_count = len(games)

        db.commit()
        log_run(db, "ingest_mlb_schedule", "success", f"games={len(games)}")
    except Exception as exc:
        db.rollback()
        log_run(db, "ingest_mlb_schedule", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
