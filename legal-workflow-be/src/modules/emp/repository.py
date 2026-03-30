"""EMP repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.emp.model import EMP
from src.config.database import get_db


def _row_to_emp(row) -> EMP:
    return EMP(
        emp_id=row["emp_id"], emp_code=row["emp_code"], emp_name=row["emp_name"],
        email=row["email"], department=row["department"], position=row["position"],
        grade_code=row["grade_code"], is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _emp_to_params(emp: EMP) -> dict:
    return {
        "emp_id": emp.emp_id, "emp_code": emp.emp_code, "emp_name": emp.emp_name,
        "email": emp.email, "department": emp.department, "position": emp.position,
        "grade_code": emp.grade_code, "is_active": int(emp.is_active),
        "created_at": emp.created_at.isoformat(), "updated_at": emp.updated_at.isoformat(),
    }


_INS = """INSERT OR IGNORE INTO emp (emp_id, emp_code, emp_name, email, department,
    position, grade_code, is_active, created_at, updated_at)
    VALUES (:emp_id, :emp_code, :emp_name, :email, :department,
            :position, :grade_code, :is_active, :created_at, :updated_at)"""


class EMPRepository:
    """SQLite EMP repository."""

    def seed(self, items: list[EMP]):
        db = get_db()
        for item in items:
            db.execute(_INS, _emp_to_params(item))
        db.commit()

    def get_all(self, department: Optional[str] = None) -> list[EMP]:
        db = get_db()
        if department:
            rows = db.execute("SELECT * FROM emp WHERE is_active=1 AND department=?", (department,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM emp WHERE is_active=1").fetchall()
        return [_row_to_emp(r) for r in rows]

    def get_by_id(self, emp_id: str) -> Optional[EMP]:
        row = get_db().execute("SELECT * FROM emp WHERE emp_id=? AND is_active=1", (emp_id,)).fetchone()
        return _row_to_emp(row) if row else None

    def get_by_code(self, emp_code: str) -> Optional[EMP]:
        row = get_db().execute("SELECT * FROM emp WHERE emp_code=? AND is_active=1", (emp_code,)).fetchone()
        return _row_to_emp(row) if row else None

    def create(self, emp: EMP) -> EMP:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _emp_to_params(emp))
        db.commit()
        return emp

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM emp")
        db.commit()


emp_repository = EMPRepository()
