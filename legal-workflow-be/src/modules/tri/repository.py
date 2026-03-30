"""TRI repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tri.model import TRI
from src.config.database import get_db


def _row_to_tri(row) -> TRI:
    return TRI(
        tri_id=row["tri_id"], trt_id=row["trt_id"], tsi_id=row["tsi_id"],
        emp_id=row["emp_id"],
        assigned_at=datetime.fromisoformat(row["assigned_at"]),
        is_active=bool(row["is_active"]),
    )


def _tri_to_params(tri: TRI) -> dict:
    return {
        "tri_id": tri.tri_id, "trt_id": tri.trt_id, "tsi_id": tri.tsi_id,
        "emp_id": tri.emp_id, "assigned_at": tri.assigned_at.isoformat(),
        "is_active": int(tri.is_active),
    }


_INS = """INSERT OR IGNORE INTO tri (tri_id, trt_id, tsi_id, emp_id, assigned_at, is_active)
    VALUES (:tri_id, :trt_id, :tsi_id, :emp_id, :assigned_at, :is_active)"""


class TRIRepository:
    """SQLite TRI repository."""

    def seed(self, items: list[TRI]):
        db = get_db()
        for item in items:
            db.execute(_INS, _tri_to_params(item))
        db.commit()

    def get_all(self) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute("SELECT * FROM tri WHERE is_active=1").fetchall()]

    def get_by_id(self, tri_id: str) -> Optional[TRI]:
        row = get_db().execute("SELECT * FROM tri WHERE tri_id=? AND is_active=1", (tri_id,)).fetchone()
        return _row_to_tri(row) if row else None

    def get_by_tsi(self, tsi_id: str) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute(
            "SELECT * FROM tri WHERE tsi_id=? AND is_active=1", (tsi_id,)).fetchall()]

    def get_by_emp(self, emp_id: str) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute(
            "SELECT * FROM tri WHERE emp_id=? AND is_active=1", (emp_id,)).fetchall()]

    def get_by_trt(self, trt_id: str) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute(
            "SELECT * FROM tri WHERE trt_id=? AND is_active=1", (trt_id,)).fetchall()]

    def get_base_pool(self) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute(
            "SELECT * FROM tri WHERE tsi_id IS NULL AND is_active=1").fetchall()]

    def get_base_pool_by_trt(self, trt_id: str) -> list[TRI]:
        return [_row_to_tri(r) for r in get_db().execute(
            "SELECT * FROM tri WHERE tsi_id IS NULL AND trt_id=? AND is_active=1", (trt_id,)).fetchall()]

    def exists(self, tsi_id: str, emp_id: str, trt_id: str) -> bool:
        row = get_db().execute(
            "SELECT 1 FROM tri WHERE tsi_id=? AND emp_id=? AND trt_id=? AND is_active=1",
            (tsi_id, emp_id, trt_id)).fetchone()
        return row is not None

    def create(self, tri: TRI) -> TRI:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _tri_to_params(tri))
        db.commit()
        return tri

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tri")
        db.commit()


tri_repository = TRIRepository()
