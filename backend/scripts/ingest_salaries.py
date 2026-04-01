#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from rapidfuzz import process
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal
from app.models import Player, Salary, Slate
from scripts.common import log_run


def find_player_id(db, name: str):
    players = db.execute(select(Player.id, Player.name)).all()
    lookup = {p.name: p.id for p in players}
    if name in lookup:
        return lookup[name]
    match = process.extractOne(name, list(lookup.keys()), score_cutoff=88)
    return lookup[match[0]] if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--site", required=True, choices=["dk", "fd"])
    parser.add_argument("--date", required=False, default=date.today().isoformat())
    parser.add_argument("--contest-type", default="main")
    args = parser.parse_args()

    d = date.fromisoformat(args.date)
    df = pd.read_csv(args.file)
    db = SessionLocal()

    try:
        slate = db.execute(select(Slate).where(Slate.slate_date == d, Slate.site == args.site, Slate.contest_type == args.contest_type)).scalar_one_or_none()
        if not slate:
            slate = Slate(slate_date=d, site=args.site, contest_type=args.contest_type, game_count=0)
            db.add(slate)
            db.flush()

        inserted, unmatched = 0, []
        for _, r in df.iterrows():
            name = str(r["Name"]) if args.site == "dk" else str(r["Nickname"])
            pid = find_player_id(db, name)
            if not pid:
                unmatched.append(name)
                continue
            exists = db.execute(select(Salary).where(Salary.slate_id == slate.id, Salary.player_id == pid)).scalar_one_or_none()
            if exists:
                continue
            if args.site == "dk":
                db.add(Salary(slate_id=slate.id, player_id=pid, salary=int(r["Salary"]), team_code=str(r.get("TeamAbbrev", "")), roster_position=str(r.get("Position", ""))))
            else:
                db.add(Salary(slate_id=slate.id, player_id=pid, salary=int(r["Salary"]), team_code=str(r.get("Team", "")), roster_position=str(r.get("Position", ""))))
            inserted += 1

        db.commit()
        msg = f"inserted={inserted} unmatched={len(unmatched)}"
        print(msg)
        if unmatched:
            Path("uploads/unmatched_players.csv").parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"name": unmatched}).to_csv("uploads/unmatched_players.csv", index=False)
        log_run(db, "ingest_salaries", "success", msg)
    except Exception as exc:
        db.rollback()
        log_run(db, "ingest_salaries", "error", str(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
