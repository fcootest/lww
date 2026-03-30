"""TDI repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tdi.model import TDI
from src.config.database import get_db


def _row_to_tdi(row) -> TDI:
    return TDI(
        tdi_id=row["tdi_id"], tdt_id=row["tdt_id"], tsi_id=row["tsi_id"],
        file_name=row["file_name"], file_url=row["file_url"],
        file_size_bytes=row["file_size_bytes"], version=row["version"],
        uploaded_by=row["uploaded_by"],
        uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
        status=row["status"], notes=row["notes"],
    )


def _tdi_to_params(tdi: TDI) -> dict:
    return {
        "tdi_id": tdi.tdi_id, "tdt_id": tdi.tdt_id, "tsi_id": tdi.tsi_id,
        "file_name": tdi.file_name, "file_url": tdi.file_url,
        "file_size_bytes": tdi.file_size_bytes, "version": tdi.version,
        "uploaded_by": tdi.uploaded_by, "uploaded_at": tdi.uploaded_at.isoformat(),
        "status": tdi.status.value if hasattr(tdi.status, "value") else tdi.status,
        "notes": tdi.notes,
    }


class TDIRepository:
    """SQLite TDI repository."""

    def get_by_tsi(self, tsi_id: str) -> list[TDI]:
        rows = get_db().execute(
            "SELECT * FROM tdi WHERE tsi_id=? AND status!='DELETED'", (tsi_id,)).fetchall()
        return [_row_to_tdi(r) for r in rows]

    def get_by_tsi_ids(self, tsi_ids: list[str]) -> list[TDI]:
        if not tsi_ids:
            return []
        db = get_db()
        ph = ",".join("?" * len(tsi_ids))
        rows = db.execute(
            f"SELECT * FROM tdi WHERE tsi_id IN ({ph}) AND status!='DELETED'", tsi_ids).fetchall()
        return [_row_to_tdi(r) for r in rows]

    def get_by_id(self, tdi_id: str) -> Optional[TDI]:
        row = get_db().execute("SELECT * FROM tdi WHERE tdi_id=?", (tdi_id,)).fetchone()
        return _row_to_tdi(row) if row else None

    def get_max_version(self, tsi_id: str, tdt_id: str) -> int:
        row = get_db().execute(
            "SELECT MAX(version) as mv FROM tdi WHERE tsi_id=? AND tdt_id=?",
            (tsi_id, tdt_id)).fetchone()
        return row["mv"] or 0

    def create(self, tdi: TDI) -> TDI:
        db = get_db()
        p = _tdi_to_params(tdi)
        db.execute("""INSERT INTO tdi (tdi_id, tdt_id, tsi_id, file_name, file_url,
            file_size_bytes, version, uploaded_by, uploaded_at, status, notes)
            VALUES (:tdi_id, :tdt_id, :tsi_id, :file_name, :file_url,
                    :file_size_bytes, :version, :uploaded_by, :uploaded_at, :status, :notes)""", p)
        db.commit()
        return tdi

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tdi")
        db.commit()


tdi_repository = TDIRepository()
