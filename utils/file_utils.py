"""
file_utils.py
==============
Filesystem helpers: safe saving of uploads, duplicate detection via
content hash, directory helpers, listing, and metadata (used by both
the Upload Documents and Knowledge Base pages' file-management tables).
"""

import hashlib
import os
import shutil
from datetime import datetime
from typing import List, Optional

from utils.config_loader import resolve_path
from utils.logger import get_logger

logger = get_logger(__name__)


def ensure_dir_exists(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_file_hash(file_bytes: bytes) -> str:
    """SHA-256 hex digest, used to detect duplicate uploads regardless of filename."""
    return hashlib.sha256(file_bytes).hexdigest()


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = original_name.replace(" ", "_")
    return f"{timestamp}_{safe_name}"


def save_uploaded_file(file_bytes: bytes, original_filename: str, category: str,
                        base_dir: str = "uploads") -> str:
    dest_dir = resolve_path(base_dir, category)
    ensure_dir_exists(dest_dir)
    unique_name = generate_unique_filename(original_filename)
    dest_path = os.path.join(dest_dir, unique_name)
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    logger.info("Saved uploaded file '%s' -> '%s' (category=%s)", original_filename, dest_path, category)
    return dest_path


def copy_to_knowledge_base(source_path: str, category: str) -> str:
    dest_dir = resolve_path("knowledge_base", category)
    ensure_dir_exists(dest_dir)
    filename = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(source_path, dest_path)
    logger.info("Promoted '%s' into knowledge_base/%s/", filename, category)
    return dest_path


def list_files(folder: str, extensions: Optional[List[str]] = None) -> List[str]:
    results = []
    if not os.path.isdir(folder):
        return results
    for root, _dirs, files in os.walk(folder):
        for fname in files:
            if fname.startswith("."):
                continue
            if extensions and get_file_extension(fname) not in extensions:
                continue
            results.append(os.path.join(root, fname))
    return results


def delete_file(path: str) -> bool:
    if os.path.exists(path):
        os.remove(path)
        logger.info("Deleted file '%s'", path)
        return True
    logger.warning("Attempted to delete non-existent file '%s'", path)
    return False


def rename_file(path: str, new_name: str) -> str:
    """Renames a file in-place (keeps the same folder), used by the Knowledge Base file-management panel."""
    directory = os.path.dirname(path)
    ext = get_file_extension(path)
    safe_new_name = new_name if new_name.lower().endswith(ext) else f"{new_name}{ext}"
    new_path = os.path.join(directory, safe_new_name)
    os.rename(path, new_path)
    logger.info("Renamed '%s' -> '%s'", path, new_path)
    return new_path


def get_file_size_mb(path: str) -> float:
    return os.path.getsize(path) / (1024 * 1024)


def get_file_metadata(path: str) -> dict:
    stat = os.stat(path)
    return {
        "filename": os.path.basename(path),
        "path": path,
        "size_mb": round(stat.st_size / (1024 * 1024), 3),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
    }


def get_folder_size_mb(folder: str) -> float:
    """Total size in MB of every file under `folder` (recursively) - used for the 'Storage Used' metric."""
    total = 0
    for path in list_files(folder):
        try:
            total += os.path.getsize(path)
        except OSError:
            continue
    return round(total / (1024 * 1024), 2)
