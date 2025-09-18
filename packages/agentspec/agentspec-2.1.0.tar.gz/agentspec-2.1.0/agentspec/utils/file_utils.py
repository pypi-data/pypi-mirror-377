"""
File utilities for AgentSpec.

Provides file operations, path handling, and file system utilities.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


class FileUtils:
    """Utility class for file operations."""

    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if it doesn't."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def read_file(path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read file content as string."""
        with open(path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_file(
        path: Union[str, Path], content: str, encoding: str = "utf-8"
    ) -> None:
        """Write content to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def read_json(path: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            result = json.load(f)
            if not isinstance(result, dict):
                raise ValueError(f"Expected JSON object, got {type(result)}")
            return result

    @staticmethod
    def write_json(
        path: Union[str, Path], data: Dict[str, Any], indent: int = 2
    ) -> None:
        """Write data to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def read_yaml(path: Union[str, Path]) -> Dict[str, Any]:
        """Read YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def write_yaml(path: Union[str, Path], data: Dict[str, Any]) -> None:
        """Write data to YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    @staticmethod
    def find_files(
        directory: Union[str, Path], pattern: str = "*", recursive: bool = True
    ) -> List[Path]:
        """Find files matching pattern in directory."""
        directory = Path(directory)
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))

    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy file from source to destination."""
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    @staticmethod
    def copy_directory(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy directory from source to destination."""
        shutil.copytree(src, dst, dirs_exist_ok=True)

    @staticmethod
    def remove_file(path: Union[str, Path]) -> None:
        """Remove file if it exists."""
        path = Path(path)
        if path.exists():
            path.unlink()

    @staticmethod
    def remove_directory(path: Union[str, Path]) -> None:
        """Remove directory and all contents."""
        path = Path(path)
        if path.exists():
            shutil.rmtree(path)

    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """Get file size in bytes."""
        return Path(path).stat().st_size

    @staticmethod
    def is_text_file(path: Union[str, Path]) -> bool:
        """Check if file is likely a text file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, IOError):
            return False

    @staticmethod
    def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> Path:
        """Get relative path from base directory."""
        return Path(path).relative_to(base)

    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize path (resolve symlinks, relative paths, etc.)."""
        return Path(path).resolve()


def get_file_hash(path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.

    Args:
        path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()
