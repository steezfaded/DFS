from datetime import date
from pydantic import BaseModel


class OverviewResponse(BaseModel):
    slate_date: date
    site: str
    top_pitchers: list[dict]
    top_values: list[dict]
    top_stacks: list[dict]
    top_one_offs: list[dict]
    refreshed_at: str | None = None


class SalaryImportResult(BaseModel):
    inserted: int
    unmatched: list[dict]
