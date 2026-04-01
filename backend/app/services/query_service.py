from __future__ import annotations

from datetime import date
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import (
    HitterMetricDaily,
    PitcherMetricDaily,
    Player,
    RefreshLog,
    Salary,
    Slate,
    StackScoreDaily,
    Team,
    TeamMetricDaily,
)


def latest_refresh(db: Session) -> str | None:
    q = select(RefreshLog).order_by(desc(RefreshLog.run_at)).limit(1)
    log = db.execute(q).scalar_one_or_none()
    return log.run_at.isoformat() if log else None


def get_hitter_rows(db: Session, slate_date: date, site: str) -> list[dict]:
    q = (
        select(HitterMetricDaily, Player, Team, Salary)
        .join(Player, Player.id == HitterMetricDaily.player_id)
        .join(Team, Team.id == Player.team_id, isouter=True)
        .join(Slate, (Slate.slate_date == HitterMetricDaily.metric_date) & (Slate.site == site), isouter=True)
        .join(Salary, (Salary.player_id == Player.id) & (Salary.slate_id == Slate.id), isouter=True)
        .where(HitterMetricDaily.metric_date == slate_date)
    )
    rows = db.execute(q).all()
    return [
        {
            "player_id": p.id,
            "name": p.name,
            "team": t.code if t else None,
            "salary": s.salary if s else None,
            "projection": h.projection,
            "ceiling": h.ceiling,
            "value_score": h.value_score,
            "leverage_score": h.leverage_score,
            "order": h.batting_order,
        }
        for h, p, t, s in rows
    ]


def get_pitcher_rows(db: Session, slate_date: date, site: str) -> list[dict]:
    q = (
        select(PitcherMetricDaily, Player, Team, Salary)
        .join(Player, Player.id == PitcherMetricDaily.player_id)
        .join(Team, Team.id == Player.team_id, isouter=True)
        .join(Slate, (Slate.slate_date == PitcherMetricDaily.metric_date) & (Slate.site == site), isouter=True)
        .join(Salary, (Salary.player_id == Player.id) & (Salary.slate_id == Slate.id), isouter=True)
        .where(PitcherMetricDaily.metric_date == slate_date)
    )
    rows = db.execute(q).all()
    return [
        {
            "player_id": p.id,
            "name": p.name,
            "team": t.code if t else None,
            "salary": s.salary if s else None,
            "projection": m.projection,
            "ceiling": m.ceiling,
            "value_score": m.value_score,
            "cash_safety": m.cash_safety,
            "gpp_upside": m.gpp_upside,
        }
        for m, p, t, s in rows
    ]


def get_stack_rows(db: Session, slate_date: date, site: str) -> list[dict]:
    q = (
        select(StackScoreDaily, Team)
        .join(Team, Team.id == StackScoreDaily.team_id)
        .where(StackScoreDaily.score_date == slate_date, StackScoreDaily.site == site)
        .order_by(desc(StackScoreDaily.stack_score))
    )
    rows = db.execute(q).all()
    return [
        {
            "team": t.code,
            "stack_score": s.stack_score,
            "ceiling_score": s.ceiling_score,
            "value_score": s.value_score,
            "ownership_proxy": s.ownership_proxy,
            "leverage_score": s.leverage_score,
            "mini_stack_score": s.mini_stack_score,
            "one_off_score": s.one_off_score,
            "salary_estimate": s.salary_estimate,
        }
        for s, t in rows
    ]


def get_team_metrics(db: Session, slate_date: date) -> list[dict]:
    q = select(TeamMetricDaily, Team).join(Team, Team.id == TeamMetricDaily.team_id).where(TeamMetricDaily.metric_date == slate_date)
    rows = db.execute(q).all()
    return [{"team": t.code, "woba": m.woba, "iso": m.iso, "bullpen_weakness": m.bullpen_weakness} for m, t in rows]
