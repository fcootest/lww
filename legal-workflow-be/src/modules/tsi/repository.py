"""TSI repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tsi.model import TSI
from src.config.database import get_db


def _row_to_tsi(row) -> TSI:
    return TSI(
        tsi_id=row["tsi_id"], tsi_code=row["tsi_code"], tst_id=row["tst_id"],
        my_parent_task=row["my_parent_task"], title=row["title"],
        description=row["description"], status=row["status"], priority=row["priority"],
        requested_by=row["requested_by"], assigned_to=row["assigned_to"],
        due_date=row["due_date"], actual_completion_date=row["actual_completion_date"],
        current_tst_level=row["current_tst_level"], current_tst_id=row["current_tst_id"],
        metadata=row["metadata"] if "metadata" in row.keys() else None,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _tsi_to_params(tsi: TSI) -> dict:
    return {
        "tsi_id": tsi.tsi_id, "tsi_code": tsi.tsi_code, "tst_id": tsi.tst_id,
        "my_parent_task": tsi.my_parent_task, "title": tsi.title,
        "description": tsi.description,
        "status": tsi.status.value if hasattr(tsi.status, "value") else tsi.status,
        "priority": tsi.priority.value if hasattr(tsi.priority, "value") and tsi.priority else tsi.priority,
        "requested_by": tsi.requested_by, "assigned_to": tsi.assigned_to,
        "due_date": tsi.due_date, "actual_completion_date": tsi.actual_completion_date,
        "current_tst_level": tsi.current_tst_level, "current_tst_id": tsi.current_tst_id,
        "metadata": tsi.metadata,
        "created_at": tsi.created_at.isoformat(), "updated_at": tsi.updated_at.isoformat(),
    }


_INS = """INSERT INTO tsi (tsi_id, tsi_code, tst_id, my_parent_task, title, description,
    status, priority, requested_by, assigned_to, due_date, actual_completion_date,
    current_tst_level, current_tst_id, metadata, created_at, updated_at)
    VALUES (:tsi_id, :tsi_code, :tst_id, :my_parent_task, :title, :description,
            :status, :priority, :requested_by, :assigned_to, :due_date, :actual_completion_date,
            :current_tst_level, :current_tst_id, :metadata, :created_at, :updated_at)"""


class TSIRepository:
    """SQLite TSI repository."""

    def get_all(self) -> list[TSI]:
        return [_row_to_tsi(r) for r in get_db().execute("SELECT * FROM tsi").fetchall()]

    def get_by_id(self, tsi_id: str) -> Optional[TSI]:
        row = get_db().execute("SELECT * FROM tsi WHERE tsi_id=?", (tsi_id,)).fetchone()
        return _row_to_tsi(row) if row else None

    def create(self, tsi: TSI) -> TSI:
        db = get_db()
        db.execute(_INS, _tsi_to_params(tsi))
        db.commit()
        return tsi

    def update(self, tsi_id: str, updates: dict) -> Optional[TSI]:
        db = get_db()
        row = db.execute("SELECT * FROM tsi WHERE tsi_id=?", (tsi_id,)).fetchone()
        if not row:
            return None
        data = _row_to_tsi(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TSI(**data)
        p = _tsi_to_params(updated)
        db.execute("""UPDATE tsi SET tsi_code=:tsi_code, tst_id=:tst_id,
            my_parent_task=:my_parent_task, title=:title, description=:description,
            status=:status, priority=:priority, requested_by=:requested_by,
            assigned_to=:assigned_to, due_date=:due_date,
            actual_completion_date=:actual_completion_date,
            current_tst_level=:current_tst_level, current_tst_id=:current_tst_id,
            metadata=:metadata,
            updated_at=:updated_at WHERE tsi_id=:tsi_id""", p)
        db.commit()
        return updated

    def next_counter(self) -> int:
        db = get_db()
        db.execute("UPDATE tsi_counter SET counter = counter + 1 WHERE id = 1")
        db.commit()
        row = db.execute("SELECT counter FROM tsi_counter WHERE id = 1").fetchone()
        return row[0]

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tsi")
        db.execute("UPDATE tsi_counter SET counter = 0 WHERE id = 1")
        db.commit()


tsi_repository = TSIRepository()
