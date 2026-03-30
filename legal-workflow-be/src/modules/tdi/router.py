"""TDI router -- document upload APIs with real file storage."""

import os
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error
from src.modules.tdi.model import TDI
from src.modules.tdi.repository import tdi_repository
from src.modules.tdi.schema import TDICreateRequest
from src.modules.tsi.repository import tsi_repository
from src.modules.tsev.model import TSEV, TSEVEventType
from src.modules.tsev.repository import tsev_repository

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/api/legal/task",
    tags=["TDI Documents"],
)


@router.post("/{tsi_id}/document")
async def upload_document(tsi_id: str, req: TDICreateRequest, user: dict = Depends(get_current_user)):
    """Upload a document (URL-based) to a task."""
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi is None:
        return send_error(message=f"TSI '{tsi_id}' not found", status_code=404)

    current_max = tdi_repository.get_max_version(tsi_id, req.tdt_id)
    version = current_max + 1

    tdi_id = f"TDI-{uuid4().hex[:8]}"
    tdi = TDI(
        tdi_id=tdi_id,
        tdt_id=req.tdt_id,
        tsi_id=tsi_id,
        file_name=req.file_name,
        file_url=req.file_url,
        version=version,
        uploaded_by=user.get("emp_code", "SYSTEM"),
        notes=req.notes,
    )
    tdi_repository.create(tdi)

    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=TSEVEventType.UPLOAD,
        emp_id=user.get("emp_code", "SYSTEM"),
        tdi_id=tdi_id,
    )
    tsev_repository.create(tsev)

    return send_success(data=tdi.model_dump(mode="json"), message="Document uploaded", status_code=201)


@router.post("/{tsi_id}/upload-file")
async def upload_file(
    tsi_id: str,
    file: UploadFile = File(...),
    tdt_id: str = Form(default="TDT-001"),
    user: dict = Depends(get_current_user),
):
    """Upload a real file to server storage."""
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi is None:
        return send_error(message=f"TSI '{tsi_id}' not found", status_code=404)

    # Save file to uploads/{tsi_id}/
    task_dir = os.path.join(UPLOAD_DIR, tsi_id)
    os.makedirs(task_dir, exist_ok=True)

    # Unique filename to avoid collisions
    ext = os.path.splitext(file.filename or "file")[1]
    stored_name = f"{uuid4().hex[:8]}{ext}"
    file_path = os.path.join(task_dir, stored_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Create TDI record
    current_max = tdi_repository.get_max_version(tsi_id, tdt_id)
    version = current_max + 1

    tdi_id_val = f"TDI-{uuid4().hex[:8]}"
    file_url = f"/api/legal/task/{tsi_id}/file/{stored_name}"

    tdi = TDI(
        tdi_id=tdi_id_val,
        tdt_id=tdt_id,
        tsi_id=tsi_id,
        file_name=file.filename or "unknown",
        file_url=file_url,
        file_size_bytes=len(content),
        version=version,
        uploaded_by=user.get("emp_code", "SYSTEM"),
    )
    tdi_repository.create(tdi)

    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=TSEVEventType.UPLOAD,
        emp_id=user.get("emp_code", "SYSTEM"),
        tdi_id=tdi_id_val,
    )
    tsev_repository.create(tsev)

    return send_success(data=tdi.model_dump(mode="json"), message="File uploaded", status_code=201)


@router.get("/{tsi_id}/file/{filename}")
async def serve_file(tsi_id: str, filename: str):
    """Serve an uploaded file."""
    file_path = os.path.join(UPLOAD_DIR, tsi_id, filename)
    if not os.path.exists(file_path):
        return send_error(message="File not found", status_code=404)
    return FileResponse(file_path)


@router.get("/{tsi_id}/documents")
async def list_documents(tsi_id: str, user: dict = Depends(get_current_user)):
    """List documents for a task."""
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi is None:
        return send_error(message=f"TSI '{tsi_id}' not found", status_code=404)
    docs = tdi_repository.get_by_tsi(tsi_id)
    return send_success(data=[d.model_dump(mode="json") for d in docs])


@router.delete("/{tsi_id}/document/{tdi_id}")
async def delete_document(tsi_id: str, tdi_id: str, user: dict = Depends(get_current_user)):
    """Soft-delete a document."""
    from src.config.database import get_db
    tdi = tdi_repository.get_by_id(tdi_id)
    if tdi is None:
        return send_error(message="Document not found", status_code=404)
    if tdi.tsi_id != tsi_id:
        return send_error(message="Document does not belong to this task", status_code=400)
    db = get_db()
    db.execute("UPDATE tdi SET status='DELETED' WHERE tdi_id=?", (tdi_id,))
    db.commit()
    return send_success(data=None, message="Document deleted")
