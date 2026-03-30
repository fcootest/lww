"""TSEV repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tsev.model import TSEV
from src.config.database import get_db


def _row_to_tsev(row) -> TSEV:
    return TSEV(
        tsev_id=row["tsev_id"], tsi_id=row["tsi_id"],
        event_type=row["event_type"], emp_id=row["emp_id"],
        event_data=row["event_data"], tdi_id=row["tdi_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _tsev_to_params(tsev: TSEV) -> dict:
    return {
        "tsev_id": tsev.tsev_id, "tsi_id": tsev.tsi_id,
        "event_type": tsev.event_type.value if hasattr(tsev.event_type, "value") else tsev.event_type,
        "emp_id": tsev.emp_id, "event_data": tsev.event_data,
        "tdi_id": tsev.tdi_id, "created_at": tsev.created_at.isoformat(),
    }


class TSEVRepository:
    """SQLite TSEV repository."""

    def get_by_tsi(self, tsi_id: str) -> list[TSEV]:
        return [_row_to_tsev(r) for r in get_db().execute(
            "SELECT * FROM tsev WHERE tsi_id=?", (tsi_id,)).fetchall()]

    def get_by_tsi_ids(self, tsi_ids: list[str]) -> list[TSEV]:
        if not tsi_ids:
            return []
        db = get_db()
        ph = ",".join("?" * len(tsi_ids))
        return [_row_to_tsev(r) for r in db.execute(
            f"SELECT * FROM tsev WHERE tsi_id IN ({ph})", tsi_ids).fetchall()]

    def get_by_id(self, tsev_id: str) -> Optional[TSEV]:
        row = get_db().execute("SELECT * FROM tsev WHERE tsev_id=?", (tsev_id,)).fetchone()
        return _row_to_tsev(row) if row else None

    def create(self, tsev: TSEV) -> TSEV:
        db = get_db()
        p = _tsev_to_params(tsev)
        db.execute("""INSERT INTO tsev (tsev_id, tsi_id, event_type, emp_id, event_data, tdi_id, created_at)
            VALUES (:tsev_id, :tsi_id, :event_type, :emp_id, :event_data, :tdi_id, :created_at)""", p)
        db.commit()
        return tsev

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tsev")
        db.commit()


tsev_repository = TSEVRepository()
