import base64
import binascii

from fastapi import HTTPException

MAX_ATTACHMENTS = 5
MAX_FILE_BYTES = 5 * 1024 * 1024


def decode_attachment(data_base64: str) -> bytes:
    try:
        raw = data_base64.split(",", 1)[-1]
        data = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(400, "첨부파일 인코딩이 올바르지 않습니다") from exc
    if not data:
        raise HTTPException(400, "빈 첨부파일은 보낼 수 없습니다")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(400, f"첨부파일은 최대 {MAX_FILE_BYTES // (1024 * 1024)}MB까지 가능합니다")
    return data


def validate_attachments(attachments: list) -> None:
    if len(attachments) > MAX_ATTACHMENTS:
        raise HTTPException(400, f"첨부파일은 최대 {MAX_ATTACHMENTS}개까지 가능합니다")
