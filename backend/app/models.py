from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    park: Mapped[str | None] = mapped_column(String(128), nullable=True)
    park_factor: Mapped[float] = mapped_column(Float, default=1.0)


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mlbam_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    bats: Mapped[str | None] = mapped_column(String(1), nullable=True)
    throws: Mapped[str | None] = mapped_column(String(1), nullable=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    positions: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_pitcher: Mapped[bool] = mapped_column(Boolean, default=False)

    team = relationship("Team")


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_date: Mapped[date] = mapped_column(Date, index=True)
    start_time_utc: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    probable_pitcher_away_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    probable_pitcher_home_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    weather_summary: Mapped[str | None] = mapped_column(String(256), nullable=True)
    run_env_score: Mapped[float] = mapped_column(Float, default=0.0)


class Slate(Base):
    __tablename__ = "slates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slate_date: Mapped[date] = mapped_column(Date, index=True)
    site: Mapped[str] = mapped_column(String(16), index=True)
    contest_type: Mapped[str] = mapped_column(String(32), default="gpp")
    game_count: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("slate_date", "site", "contest_type", name="uq_slate"),)


class Salary(Base):
    __tablename__ = "salaries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slate_id: Mapped[int] = mapped_column(ForeignKey("slates.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    team_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    opponent_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    roster_position: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salary: Mapped[int] = mapped_column(Integer, index=True)
    projected_ownership_proxy: Mapped[float] = mapped_column(Float, default=0.0)
    __table_args__ = (UniqueConstraint("slate_id", "player_id", name="uq_slate_player_salary"),)


class HitterMetricDaily(Base):
    __tablename__ = "hitter_metrics_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_date: Mapped[date] = mapped_column(Date, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    opponent_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    batting_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pa_proj: Mapped[float] = mapped_column(Float, default=4.2)
    woba: Mapped[float] = mapped_column(Float, default=0.0)
    xwoba: Mapped[float] = mapped_column(Float, default=0.0)
    iso: Mapped[float] = mapped_column(Float, default=0.0)
    barrel_pct: Mapped[float] = mapped_column(Float, default=0.0)
    hard_hit_pct: Mapped[float] = mapped_column(Float, default=0.0)
    k_pct: Mapped[float] = mapped_column(Float, default=0.0)
    bb_pct: Mapped[float] = mapped_column(Float, default=0.0)
    recent_form: Mapped[float] = mapped_column(Float, default=0.0)
    projection: Mapped[float] = mapped_column(Float, default=0.0)
    floor: Mapped[float] = mapped_column(Float, default=0.0)
    ceiling: Mapped[float] = mapped_column(Float, default=0.0)
    value_score: Mapped[float] = mapped_column(Float, default=0.0)
    leverage_score: Mapped[float] = mapped_column(Float, default=0.0)


class PitcherMetricDaily(Base):
    __tablename__ = "pitcher_metrics_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_date: Mapped[date] = mapped_column(Date, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    opponent_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    ip_proj: Mapped[float] = mapped_column(Float, default=5.5)
    k_pct: Mapped[float] = mapped_column(Float, default=0.0)
    bb_pct: Mapped[float] = mapped_column(Float, default=0.0)
    k_minus_bb: Mapped[float] = mapped_column(Float, default=0.0)
    xera: Mapped[float] = mapped_column(Float, default=0.0)
    xwoba_allowed: Mapped[float] = mapped_column(Float, default=0.0)
    hard_hit_allowed: Mapped[float] = mapped_column(Float, default=0.0)
    swstr_pct: Mapped[float] = mapped_column(Float, default=0.0)
    csw_pct: Mapped[float] = mapped_column(Float, default=0.0)
    projection: Mapped[float] = mapped_column(Float, default=0.0)
    floor: Mapped[float] = mapped_column(Float, default=0.0)
    ceiling: Mapped[float] = mapped_column(Float, default=0.0)
    value_score: Mapped[float] = mapped_column(Float, default=0.0)
    leverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    cash_safety: Mapped[float] = mapped_column(Float, default=0.0)
    gpp_upside: Mapped[float] = mapped_column(Float, default=0.0)


class TeamMetricDaily(Base):
    __tablename__ = "team_metrics_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_date: Mapped[date] = mapped_column(Date, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    woba: Mapped[float] = mapped_column(Float, default=0.0)
    iso: Mapped[float] = mapped_column(Float, default=0.0)
    k_pct: Mapped[float] = mapped_column(Float, default=0.0)
    bb_pct: Mapped[float] = mapped_column(Float, default=0.0)
    hard_hit_pct: Mapped[float] = mapped_column(Float, default=0.0)
    barrel_pct: Mapped[float] = mapped_column(Float, default=0.0)
    runs_per_game_14: Mapped[float] = mapped_column(Float, default=0.0)
    bullpen_weakness: Mapped[float] = mapped_column(Float, default=0.0)


class StackScoreDaily(Base):
    __tablename__ = "stack_scores_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score_date: Mapped[date] = mapped_column(Date, index=True)
    site: Mapped[str] = mapped_column(String(16), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    opponent_pitcher_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    stack_score: Mapped[float] = mapped_column(Float, default=0.0)
    ceiling_score: Mapped[float] = mapped_column(Float, default=0.0)
    value_score: Mapped[float] = mapped_column(Float, default=0.0)
    ownership_proxy: Mapped[float] = mapped_column(Float, default=0.0)
    leverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    top5_projection: Mapped[float] = mapped_column(Float, default=0.0)
    salary_estimate: Mapped[int] = mapped_column(Integer, default=0)
    mini_stack_score: Mapped[float] = mapped_column(Float, default=0.0)
    one_off_score: Mapped[float] = mapped_column(Float, default=0.0)


class RefreshLog(Base):
    __tablename__ = "refresh_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    script_name: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)


Index("idx_hitter_date_player", HitterMetricDaily.metric_date, HitterMetricDaily.player_id)
Index("idx_pitcher_date_player", PitcherMetricDaily.metric_date, PitcherMetricDaily.player_id)
Index("idx_stack_date_site", StackScoreDaily.score_date, StackScoreDaily.site)
