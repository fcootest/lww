"""TNT repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tnt.model import TNT
from src.config.database import get_db


def _row_to_tnt(row) -> TNT:
    return TNT(
        tnt_id=row["tnt_id"], from_tst_id=row["from_tst_id"], to_tst_id=row["to_tst_id"],
        condition_expression=row["condition_expression"],
        condition_description=row["condition_description"],
        priority=row["priority"], is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _tnt_to_params(tnt: TNT) -> dict:
    return {
        "tnt_id": tnt.tnt_id, "from_tst_id": tnt.from_tst_id, "to_tst_id": tnt.to_tst_id,
        "condition_expression": tnt.condition_expression,
        "condition_description": tnt.condition_description,
        "priority": tnt.priority, "is_active": int(tnt.is_active),
        "created_at": tnt.created_at.isoformat(), "updated_at": tnt.updated_at.isoformat(),
    }


_INS = """INSERT OR IGNORE INTO tnt (tnt_id, from_tst_id, to_tst_id, condition_expression,
    condition_description, priority, is_active, created_at, updated_at)
    VALUES (:tnt_id, :from_tst_id, :to_tst_id, :condition_expression,
            :condition_description, :priority, :is_active, :created_at, :updated_at)"""


class TNTRepository:
    """SQLite TNT repository."""

    def seed(self, items: list[TNT]):
        db = get_db()
        for item in items:
            db.execute(_INS, _tnt_to_params(item))
        db.commit()

    def get_all(self, from_tst_id: Optional[str] = None) -> list[TNT]:
        db = get_db()
        if from_tst_id:
            rows = db.execute("SELECT * FROM tnt WHERE is_active=1 AND from_tst_id=?", (from_tst_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM tnt WHERE is_active=1").fetchall()
        return [_row_to_tnt(r) for r in rows]

    def get_by_id(self, tnt_id: str) -> Optional[TNT]:
        row = get_db().execute("SELECT * FROM tnt WHERE tnt_id=? AND is_active=1", (tnt_id,)).fetchone()
        return _row_to_tnt(row) if row else None

    def create(self, tnt: TNT) -> TNT:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _tnt_to_params(tnt))
        db.commit()
        return tnt

    def update(self, tnt_id: str, updates: dict) -> Optional[TNT]:
        db = get_db()
        row = db.execute("SELECT * FROM tnt WHERE tnt_id=?", (tnt_id,)).fetchone()
        if not row:
            return None
        data = _row_to_tnt(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TNT(**data)
        p = _tnt_to_params(updated)
        db.execute("""UPDATE tnt SET from_tst_id=:from_tst_id, to_tst_id=:to_tst_id,
            condition_expression=:condition_expression, condition_description=:condition_description,
            priority=:priority, is_active=:is_active, updated_at=:updated_at WHERE tnt_id=:tnt_id""", p)
        db.commit()
        return updated

    def delete(self, tnt_id: str) -> bool:
        row = get_db().execute("SELECT 1 FROM tnt WHERE tnt_id=?", (tnt_id,)).fetchone()
        if not row:
            return False
        self.update(tnt_id, {"is_active": False})
        return True

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tnt")
        db.commit()


tnt_repository = TNTRepository()
