from __future__ import annotations

from datetime import date
import io
import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Player, Salary, Slate, Team
from .schemas import OverviewResponse, SalaryImportResult
from .services.query_service import (
    get_hitter_rows,
    get_pitcher_rows,
    get_stack_rows,
    get_team_metrics,
    latest_refresh,
)
from rapidfuzz import process

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MLB DFS Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def healthcheck():
    return {"ok": True}


@app.get("/api/overview", response_model=OverviewResponse)
def overview(
    slate_date: date = Query(default_factory=date.today),
    site: str = Query("dk"),
    db: Session = Depends(get_db),
):
    hitters = sorted(get_hitter_rows(db, slate_date, site), key=lambda x: x["value_score"], reverse=True)
    pitchers = sorted(get_pitcher_rows(db, slate_date, site), key=lambda x: x["projection"], reverse=True)
    stacks = get_stack_rows(db, slate_date, site)
    one_offs = sorted(hitters, key=lambda x: x["ceiling"], reverse=True)[:10]
    return OverviewResponse(
        slate_date=slate_date,
        site=site,
        top_pitchers=pitchers[:10],
        top_values=hitters[:10],
        top_stacks=stacks[:10],
        top_one_offs=one_offs,
        refreshed_at=latest_refresh(db),
    )


@app.get("/api/slate")
def slate(slate_date: date = Query(default_factory=date.today), site: str = Query("dk"), db: Session = Depends(get_db)):
    slate_q = select(Slate).where(Slate.slate_date == slate_date, Slate.site == site)
    slate_obj = db.execute(slate_q).scalar_one_or_none()
    if not slate_obj:
        return {"slate_date": slate_date, "site": site, "games": [], "warning": "No slate loaded yet"}
    return {
        "slate_date": slate_date,
        "site": site,
        "contest_type": slate_obj.contest_type,
        "game_count": slate_obj.game_count,
        "stack_rankings": get_stack_rows(db, slate_date, site)[:5],
        "top_pitchers": get_pitcher_rows(db, slate_date, site)[:5],
    }


@app.get("/api/hitters")
def hitters(slate_date: date = Query(default_factory=date.today), site: str = "dk", db: Session = Depends(get_db)):
    return get_hitter_rows(db, slate_date, site)


@app.get("/api/pitchers")
def pitchers(slate_date: date = Query(default_factory=date.today), site: str = "dk", db: Session = Depends(get_db)):
    return get_pitcher_rows(db, slate_date, site)


@app.get("/api/stacks")
def stacks(slate_date: date = Query(default_factory=date.today), site: str = "dk", db: Session = Depends(get_db)):
    return get_stack_rows(db, slate_date, site)


@app.get("/api/games")
def games(slate_date: date = Query(default_factory=date.today), db: Session = Depends(get_db)):
    return {"slate_date": slate_date, "team_context": get_team_metrics(db, slate_date)}


@app.get("/api/player/{player_id}")
def player(player_id: int, db: Session = Depends(get_db)):
    p = db.get(Player, player_id)
    if not p:
        raise HTTPException(404, "Player not found")
    return {"id": p.id, "name": p.name, "positions": p.positions, "is_pitcher": p.is_pitcher, "team_id": p.team_id}


@app.get("/api/team/{team_id}")
def team(team_id: int, db: Session = Depends(get_db)):
    t = db.get(Team, team_id)
    if not t:
        raise HTTPException(404, "Team not found")
    return {"id": t.id, "code": t.code, "name": t.name, "park_factor": t.park_factor}


def _find_player_id(db: Session, name: str) -> int | None:
    players = db.execute(select(Player.id, Player.name)).all()
    lookup = {p.name: p.id for p in players}
    if name in lookup:
        return lookup[name]
    match = process.extractOne(name, lookup.keys(), score_cutoff=88)
    return lookup[match[0]] if match else None


@app.post("/api/import/salaries", response_model=SalaryImportResult)
async def import_salaries(
    slate_date: date,
    site: str,
    contest_type: str = "main",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await file.read()
    df = pd.read_csv(io.BytesIO(raw))
    site_norm = site.lower()
    if site_norm not in {"dk", "fd"}:
        raise HTTPException(400, "site must be dk or fd")

    slate = db.execute(select(Slate).where(Slate.slate_date == slate_date, Slate.site == site_norm, Slate.contest_type == contest_type)).scalar_one_or_none()
    if not slate:
        slate = Slate(slate_date=slate_date, site=site_norm, contest_type=contest_type, game_count=0)
        db.add(slate)
        db.flush()

    rows = []
    unmatched = []
    if site_norm == "dk":
        required = {"Name", "Salary", "TeamAbbrev", "Position", "Game Info"}
        if not required.issubset(df.columns):
            raise HTTPException(400, f"DK file missing columns: {required - set(df.columns)}")
        for _, r in df.iterrows():
            pid = _find_player_id(db, str(r["Name"]))
            if not pid:
                unmatched.append({"name": r["Name"], "site": "dk"})
                continue
            opp = str(r.get("Game Info", "")).split("@")[0][:3] if "@" in str(r.get("Game Info", "")) else None
            rows.append(Salary(slate_id=slate.id, player_id=pid, salary=int(r["Salary"]), team_code=str(r["TeamAbbrev"]), opponent_code=opp, roster_position=str(r["Position"])))
    else:
        required = {"Nickname", "Salary", "Team", "Position"}
        if not required.issubset(df.columns):
            raise HTTPException(400, f"FD file missing columns: {required - set(df.columns)}")
        for _, r in df.iterrows():
            pid = _find_player_id(db, str(r["Nickname"]))
            if not pid:
                unmatched.append({"name": r["Nickname"], "site": "fd"})
                continue
            rows.append(Salary(slate_id=slate.id, player_id=pid, salary=int(r["Salary"]), team_code=str(r["Team"]), roster_position=str(r["Position"])))

    inserted = 0
    for s in rows:
        exists = db.execute(select(Salary).where(Salary.slate_id == s.slate_id, Salary.player_id == s.player_id)).scalar_one_or_none()
        if not exists:
            db.add(s)
            inserted += 1
    db.commit()
    return SalaryImportResult(inserted=inserted, unmatched=unmatched)
