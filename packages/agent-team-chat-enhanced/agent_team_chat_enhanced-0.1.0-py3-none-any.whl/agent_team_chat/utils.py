import base64
import hashlib
import json
import logging
import mimetypes
import os
import re
import time
from typing import Optional, Tuple


MAX_IMAGE_BYTES_DEFAULT = 8 * 1024 * 1024  # 8MB
ALLOWED_IMAGE_MIME = {
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "image/webp": [b"RIFF"],  # further check for WEBP in header
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def epoch_ms() -> int:
    return int(time.time() * 1000)


def json_dumps(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def safe_filename(name: str, prefix: str = "upload", suffix: str = "") -> str:
    name = name.strip() or ""
    # Remove path components
    name = os.path.basename(name)
    # Replace unsafe chars
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    # Prevent hidden or parent path
    if name.startswith("."):
        name = name.lstrip(".")
    if not name:
        name = f"{prefix}_{int(time.time())}{suffix}"
    return name


def _read_file_header(path: str, max_len: int = 16) -> bytes:
    with open(path, "rb") as f:
        return f.read(max_len)


def detect_image_mime_from_header(header: bytes) -> Optional[str]:
    for mime, magics in ALLOWED_IMAGE_MIME.items():
        for m in magics:
            if header.startswith(m):
                if mime == "image/webp":
                    # WEBP requires RIFF....WEBP
                    if len(header) >= 12 and header[8:12] == b"WEBP":
                        return mime
                else:
                    return mime
    return None


def validate_image_file(path: str, max_bytes: int = MAX_IMAGE_BYTES_DEFAULT) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return False, None, "file_not_found"
    if st.st_size > max_bytes:
        return False, None, "too_large"
    header = _read_file_header(path)
    mime = detect_image_mime_from_header(header)
    if not mime:
        # Fallback to extension-based guess, still restricted
        guessed, _ = mimetypes.guess_type(path)
        if guessed in ALLOWED_IMAGE_MIME:
            mime = guessed
        else:
            return False, None, "unsupported_type"
    return True, mime, None


def decode_base64_data(data: str) -> bytes:
    # Support data URLs and raw base64
    if data.startswith("data:"):
        try:
            header, b64data = data.split(",", 1)
        except ValueError:
            raise ValueError("invalid_data_url")
        return base64.b64decode(b64data, validate=True)
    return base64.b64decode(data, validate=True)


def write_bytes(dest_dir: str, filename_hint: str, content: bytes) -> str:
    ensure_dir(dest_dir)
    name = safe_filename(filename_hint or f"upload_{int(time.time())}")
    dest_path = os.path.join(dest_dir, name)
    # Avoid overwrite
    base, ext = os.path.splitext(dest_path)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = f"{base}_{counter}{ext}"
        counter += 1
    with open(dest_path, "wb") as f:
        f.write(content)
    return dest_path


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AppError(Exception):
    def __init__(self, code: str, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retry_after = retry_after

    def to_dict(self):
        err = {"code": self.code, "message": self.message}
        if self.retry_after is not None:
            err["retry_after"] = self.retry_after
        return err


def configure_logging(json_mode: bool = False):
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    if json_mode:
        class JsonLogFormatter(logging.Formatter):
            def format(self, record):
                payload = {
                    "level": record.levelname,
                    "time": int(time.time()),
                    "msg": record.getMessage(),
                    "name": record.name,
                }
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                return json_dumps(payload)

        handler = logging.StreamHandler()
        handler.setFormatter(JsonLogFormatter())
        root = logging.getLogger()
        root.handlers = [handler]
        root.setLevel(level)
    else:
        logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
