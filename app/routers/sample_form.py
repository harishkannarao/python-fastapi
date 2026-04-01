import os
from typing import List, Optional

import aiofiles
import structlog
from fastapi import APIRouter
from fastapi import UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from starlette import status

from app.config import settings

router = APIRouter(prefix="/file-transfer", tags=["files"])


@router.post("/form-submit", status_code=status.HTTP_303_SEE_OTHER)
async def handle_form(
    first_name: Optional[str] = Form(None, alias="firstName"),
    last_name: Optional[str] = Form(None, alias="lastName"),
    files: Optional[List[UploadFile]] = File(None),
):
    logger = structlog.get_logger()
    logger.info(f"Upload Location: {os.path.abspath(settings.app_file_upload_path)}")
    logger.info(f"Text fields: {first_name}, {last_name}")

    if files:
        for file in files:
            logger.info(f"Uploading file: {file.filename}")
            target_path: str = os.path.join(
                settings.app_file_upload_path, file.filename
            )

            # Asynchronous streaming write
            async with aiofiles.open(target_path, "wb") as out_file:
                while content := await file.read(
                    1024 * 16
                ):  # 16KB chunks like your Java code
                    await out_file.write(content)

            await file.close()

    return RedirectResponse(
        url="/context/static/sample_form_submit_success.html",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/files/{name}")
async def get_archive(name: str):
    file_path = os.path.join(settings.app_file_upload_path, name)
    logger = structlog.get_logger()
    logger.info(f"Resolved file_path: {file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # FileResponse handles the async streaming internally
    # and is already non-blocking.
    return FileResponse(
        path=file_path, filename=name, media_type="application/octet-stream"
    )
