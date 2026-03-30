"""TDTP repository — SQLite data access layer."""

import json as _json
from typing import Optional
from datetime import datetime
from src.modules.tdtp.model import TDTP
from src.config.database import get_db


def _row_to_tdtp(row) -> TDTP:
    ts = row["template_structure"]
    if ts and isinstance(ts, str):
        try: ts = _json.loads(ts)
        except Exception: pass
    sd = row["sample_data"]
    if sd and isinstance(sd, str):
        try: sd = _json.loads(sd)
        except Exception: pass
    return TDTP(
        tdtp_id=row["tdtp_id"], tdt_id=row["tdt_id"],
        tdtp_code=row["tdtp_code"], tdtp_name=row["tdtp_name"],
        description=row["description"], template_file_ref=row["template_file_ref"],
        template_structure=ts, sample_data=sd,
        version=row["version"], is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _tdtp_to_params(tdtp: TDTP) -> dict:
    return {
        "tdtp_id": tdtp.tdtp_id, "tdt_id": tdtp.tdt_id,
        "tdtp_code": tdtp.tdtp_code, "tdtp_name": tdtp.tdtp_name,
        "description": tdtp.description, "template_file_ref": tdtp.template_file_ref,
        "template_structure": _json.dumps(tdtp.template_structure) if tdtp.template_structure else None,
        "sample_data": _json.dumps(tdtp.sample_data) if tdtp.sample_data else None,
        "version": tdtp.version, "is_active": int(tdtp.is_active),
        "created_at": tdtp.created_at.isoformat(), "updated_at": tdtp.updated_at.isoformat(),
    }


_INS = """INSERT OR IGNORE INTO tdtp (tdtp_id, tdt_id, tdtp_code, tdtp_name, description,
    template_file_ref, template_structure, sample_data, version, is_active, created_at, updated_at)
    VALUES (:tdtp_id, :tdt_id, :tdtp_code, :tdtp_name, :description,
            :template_file_ref, :template_structure, :sample_data, :version, :is_active,
            :created_at, :updated_at)"""


class TDTPRepository:
    """SQLite TDTP repository."""

    def seed(self, items: list[TDTP]):
        db = get_db()
        for item in items:
            db.execute(_INS, _tdtp_to_params(item))
        db.commit()

    def get_all(self) -> list[TDTP]:
        return [_row_to_tdtp(r) for r in get_db().execute("SELECT * FROM tdtp WHERE is_active=1").fetchall()]

    def get_by_id(self, tdtp_id: str) -> Optional[TDTP]:
        row = get_db().execute("SELECT * FROM tdtp WHERE tdtp_id=? AND is_active=1", (tdtp_id,)).fetchone()
        return _row_to_tdtp(row) if row else None

    def get_by_tdt_id(self, tdt_id: str) -> Optional[TDTP]:
        row = get_db().execute("SELECT * FROM tdtp WHERE tdt_id=? AND is_active=1", (tdt_id,)).fetchone()
        return _row_to_tdtp(row) if row else None

    def create(self, tdtp: TDTP) -> TDTP:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _tdtp_to_params(tdtp))
        db.commit()
        return tdtp

    def update(self, tdtp_id: str, updates: dict) -> Optional[TDTP]:
        db = get_db()
        row = db.execute("SELECT * FROM tdtp WHERE tdtp_id=?", (tdtp_id,)).fetchone()
        if not row:
            return None
        data = _row_to_tdtp(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TDTP(**data)
        p = _tdtp_to_params(updated)
        db.execute("""UPDATE tdtp SET tdt_id=:tdt_id, tdtp_code=:tdtp_code, tdtp_name=:tdtp_name,
            description=:description, template_file_ref=:template_file_ref,
            template_structure=:template_structure, sample_data=:sample_data,
            version=:version, is_active=:is_active, updated_at=:updated_at
            WHERE tdtp_id=:tdtp_id""", p)
        db.commit()
        return updated

    def delete(self, tdtp_id: str) -> bool:
        row = get_db().execute("SELECT 1 FROM tdtp WHERE tdtp_id=?", (tdtp_id,)).fetchone()
        if not row:
            return False
        self.update(tdtp_id, {"is_active": False})
        return True

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tdtp")
        db.commit()


tdtp_repository = TDTPRepository()
