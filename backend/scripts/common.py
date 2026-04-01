from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session
from app.models import RefreshLog


def log_run(db: Session, script_name: str, status: str, message: str = "") -> None:
    db.add(RefreshLog(script_name=script_name, status=status, message=message, run_at=datetime.utcnow()))
    db.commit()
