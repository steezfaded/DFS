# MLB DFS Dashboard (DFS-first)

Production-style local MLB DFS research stack with ETL + API + Next.js dashboard focused on slate decisions, value, leverage, stacks, and roster construction.

## Architecture

- **Frontend**: Next.js + TypeScript + Tailwind + Recharts (`frontend/`)
- **Backend API**: FastAPI + SQLAlchemy (`backend/app/`)
- **ETL/Data**: Python scripts with `pybaseball`, `requests`, `pandas` (`backend/scripts/`)
- **Database**: SQLite default for local reliability (`DATABASE_URL` supports PostgreSQL)

## File Tree

```text
backend/
  app/
    main.py
    database.py
    models.py
    schemas.py
    services/query_service.py
  scripts/
    ingest_mlb_schedule.py
    ingest_statcast.py
    ingest_salaries.py
    ingest_lineups.py
    compute_dfs_hitter_metrics.py
    compute_dfs_pitcher_metrics.py
    compute_stack_scores.py
    refresh_all.py
frontend/
  app/
    page.tsx
    hitters/page.tsx
    pitchers/page.tsx
    stacks/page.tsx
    games/page.tsx
    lineup-builder/page.tsx
    player/[id]/page.tsx
  components/
```

## Data Sources

- MLB schedule: `statsapi.mlb.com`
- Statcast/season tables: `pybaseball` (`batting_stats`, `pitching_stats`)
- DFS salaries: **CSV import workflow** for DK and FD via CLI script or API endpoint

## Database Schema (core)

- `players`, `teams`, `games`, `slates`, `salaries`
- `hitter_metrics_daily`, `pitcher_metrics_daily`, `team_metrics_daily`
- `stack_scores_daily`, `refresh_logs`

Indexes included on high-volume date/player fields for slate query speed.

## Setup

### 1) Python backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

### 2) Run ETL refresh

```bash
python backend/scripts/refresh_all.py
```

### 3) Salary import (required for value calculations)

#### DraftKings

```bash
python backend/scripts/ingest_salaries.py --file /path/to/dk.csv --site dk --date 2026-04-01 --contest-type main
```

#### FanDuel

```bash
python backend/scripts/ingest_salaries.py --file /path/to/fd.csv --site fd --date 2026-04-01 --contest-type main
```

Unmatched players are written to `uploads/unmatched_players.csv` for manual resolution.

### 4) Start API

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 5) Start frontend

```bash
cd frontend
npm install
npm run dev
```


## Vercel Deployment (monorepo root)

If deploying from the repository root, Vercel must build the Next.js app from `frontend/`. This repo includes root `package.json` (with Next.js dependency for Vercel framework detection) and `vercel.json` so Preview/Production deployments build and serve the frontend correctly (avoids root 404 / no-nextjs-detected failures).
If deploying from the repository root, Vercel must build the Next.js app from `frontend/`. This repo includes root `package.json` and `vercel.json` so Preview/Production deployments build and serve the frontend correctly (avoids root 404 deployments).

## API Endpoints

- `/api/slate`
- `/api/hitters`
- `/api/pitchers`
- `/api/stacks`
- `/api/games`
- `/api/player/{id}`
- `/api/team/{id}`
- `/api/import/salaries`
- `/api/overview`

All support date/site parameters where applicable.

## Projection Methodology (transparent)

### Hitters
Projection blends season skill and DFS upside proxies:
- baseline from wRC+, power (ISO/HR), speed (SB)
- PA proxy from PA/G
- floor/ceiling bands as deterministic multipliers
- salary-adjusted value score after salary import
- leverage proxy: upside relative to salary + strikeout risk suppression

### Pitchers
Projection blends:
- K-BB% and workload proxy (IP/GS)
- floor/ceiling as spread around median projection
- value score by salary
- cash safety from floor + command
- GPP upside from ceiling + strikeout skill

### Ownership Proxy
Public ownership feed is not assumed.
Proxy uses salary, projection concentration, obvious value spots, and stack popularity bias.

### Stack Methodology
Team stacks are generated from top projected hitters per team:
- top-5 aggregate projection
- top-5 aggregate ceiling
- stack value by estimated salary
- ownership proxy + leverage differential
- mini-stack and one-off support scores

## Pages

- **Overview / Command Center**: best pitchers, values, stacks, one-offs, refresh status.
- **Hitters**: sortable DFS table + projection/salary scatter.
- **Pitchers**: projection/value/ceiling/cash/GPP matrix.
- **Stacks**: stack score, ownership proxy, leverage score.
- **Games**: team context cards with offense and bullpen indicators.
- **Player Detail**: player profile + warnings on public data latency.
- **Lineup Builder Foundation**: favorite/add players, track salary and remaining cap.

## Limitations

- Lineups/weather/umpire are intentionally pluggable and may require separate licensed/public feeds.
- Same-day probable starters and batting order can lag in public endpoints.
- Ownership is a proxy model, not a paid projection feed.
- SQLite default is local-first; PostgreSQL recommended for multi-user or large historical backfills.

## Roadmap

- Full contest-size aware ownership model calibration
- Weather + park run model improvements
- Exportable player pools / lineup rule sets
- Advanced lineup optimizer module and late-swap engine
- bullpen splits and rolling leverage index automation
