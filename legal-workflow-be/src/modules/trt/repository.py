"""TRT repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.trt.model import TRT, TST_TRT
from src.config.database import get_db


def _row_to_trt(row) -> TRT:
    return TRT(
        trt_id=row["trt_id"], trt_code=row["trt_code"], trt_name=row["trt_name"],
        description=row["description"], is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _trt_to_params(trt: TRT) -> dict:
    return {
        "trt_id": trt.trt_id, "trt_code": trt.trt_code, "trt_name": trt.trt_name,
        "description": trt.description, "is_active": int(trt.is_active),
        "created_at": trt.created_at.isoformat(), "updated_at": trt.updated_at.isoformat(),
    }


class TRTRepository:
    """SQLite TRT repository."""

    def get_all(self) -> list[TRT]:
        return [_row_to_trt(r) for r in get_db().execute("SELECT * FROM trt WHERE is_active=1").fetchall()]

    def get_by_id(self, trt_id: str) -> Optional[TRT]:
        row = get_db().execute("SELECT * FROM trt WHERE trt_id=? AND is_active=1", (trt_id,)).fetchone()
        return _row_to_trt(row) if row else None

    def create(self, trt: TRT) -> TRT:
        db = get_db()
        p = _trt_to_params(trt)
        db.execute("""INSERT OR IGNORE INTO trt (trt_id, trt_code, trt_name, description, is_active, created_at, updated_at)
            VALUES (:trt_id, :trt_code, :trt_name, :description, :is_active, :created_at, :updated_at)""", p)
        db.commit()
        return trt

    def update(self, trt_id: str, updates: dict) -> Optional[TRT]:
        db = get_db()
        row = db.execute("SELECT * FROM trt WHERE trt_id=?", (trt_id,)).fetchone()
        if not row:
            return None
        data = _row_to_trt(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TRT(**data)
        p = _trt_to_params(updated)
        db.execute("""UPDATE trt SET trt_code=:trt_code, trt_name=:trt_name,
            description=:description, is_active=:is_active, updated_at=:updated_at
            WHERE trt_id=:trt_id""", p)
        db.commit()
        return updated

    def delete(self, trt_id: str) -> bool:
        row = get_db().execute("SELECT 1 FROM trt WHERE trt_id=?", (trt_id,)).fetchone()
        if not row:
            return False
        self.update(trt_id, {"is_active": False})
        return True

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM trt")
        db.commit()


class TSTTRTRepository:
    """SQLite TST_TRT junction repository."""

    def get_by_tst(self, tst_id: str) -> list[TST_TRT]:
        rows = get_db().execute("SELECT * FROM tst_trt WHERE tst_id=?", (tst_id,)).fetchall()
        return [TST_TRT(tst_id=r["tst_id"], trt_id=r["trt_id"], is_required=bool(r["is_required"])) for r in rows]

    def get_by_trt(self, trt_id: str) -> list[TST_TRT]:
        rows = get_db().execute("SELECT * FROM tst_trt WHERE trt_id=?", (trt_id,)).fetchall()
        return [TST_TRT(tst_id=r["tst_id"], trt_id=r["trt_id"], is_required=bool(r["is_required"])) for r in rows]

    def exists(self, tst_id: str, trt_id: str) -> bool:
        return get_db().execute(
            "SELECT 1 FROM tst_trt WHERE tst_id=? AND trt_id=?", (tst_id, trt_id)).fetchone() is not None

    def create(self, mapping: TST_TRT) -> TST_TRT:
        db = get_db()
        db.execute("INSERT OR IGNORE INTO tst_trt (tst_id, trt_id, is_required) VALUES (?, ?, ?)",
            (mapping.tst_id, mapping.trt_id, int(mapping.is_required)))
        db.commit()
        return mapping

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tst_trt")
        db.commit()


trt_repository = TRTRepository()
tst_trt_repository = TSTTRTRepository()
