"""TDT repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tdt.model import TDT
from src.config.database import get_db


def _row_to_tdt(row) -> TDT:
    return TDT(
        tdt_id=row["tdt_id"], tdt_code=row["tdt_code"], tdt_name=row["tdt_name"],
        description=row["description"], file_extensions=row["file_extensions"],
        max_file_size_mb=row["max_file_size_mb"],
        is_required=bool(row["is_required"]) if row["is_required"] is not None else False,
        tdtp_id=row["tdtp_id"], is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _tdt_to_params(tdt: TDT) -> dict:
    return {
        "tdt_id": tdt.tdt_id, "tdt_code": tdt.tdt_code, "tdt_name": tdt.tdt_name,
        "description": tdt.description, "file_extensions": tdt.file_extensions,
        "max_file_size_mb": tdt.max_file_size_mb,
        "is_required": int(tdt.is_required) if tdt.is_required is not None else 0,
        "tdtp_id": tdt.tdtp_id, "is_active": int(tdt.is_active),
        "created_at": tdt.created_at.isoformat(), "updated_at": tdt.updated_at.isoformat(),
    }


_INS = """INSERT OR IGNORE INTO tdt (tdt_id, tdt_code, tdt_name, description, file_extensions,
    max_file_size_mb, is_required, tdtp_id, is_active, created_at, updated_at)
    VALUES (:tdt_id, :tdt_code, :tdt_name, :description, :file_extensions,
            :max_file_size_mb, :is_required, :tdtp_id, :is_active, :created_at, :updated_at)"""


class TDTRepository:
    """SQLite TDT repository."""

    def seed(self, items: list[TDT]):
        db = get_db()
        for item in items:
            db.execute(_INS, _tdt_to_params(item))
        db.commit()

    def get_all(self) -> list[TDT]:
        return [_row_to_tdt(r) for r in get_db().execute("SELECT * FROM tdt WHERE is_active=1").fetchall()]

    def get_by_id(self, tdt_id: str) -> Optional[TDT]:
        row = get_db().execute("SELECT * FROM tdt WHERE tdt_id=? AND is_active=1", (tdt_id,)).fetchone()
        return _row_to_tdt(row) if row else None

    def create(self, tdt: TDT) -> TDT:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _tdt_to_params(tdt))
        db.commit()
        return tdt

    def update(self, tdt_id: str, updates: dict) -> Optional[TDT]:
        db = get_db()
        row = db.execute("SELECT * FROM tdt WHERE tdt_id=?", (tdt_id,)).fetchone()
        if not row:
            return None
        data = _row_to_tdt(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TDT(**data)
        p = _tdt_to_params(updated)
        db.execute("""UPDATE tdt SET tdt_code=:tdt_code, tdt_name=:tdt_name,
            description=:description, file_extensions=:file_extensions,
            max_file_size_mb=:max_file_size_mb, is_required=:is_required,
            tdtp_id=:tdtp_id, is_active=:is_active, updated_at=:updated_at
            WHERE tdt_id=:tdt_id""", p)
        db.commit()
        return updated

    def delete(self, tdt_id: str) -> bool:
        row = get_db().execute("SELECT 1 FROM tdt WHERE tdt_id=?", (tdt_id,)).fetchone()
        if not row:
            return False
        self.update(tdt_id, {"is_active": False})
        return True

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tdt")
        db.commit()


tdt_repository = TDTRepository()
