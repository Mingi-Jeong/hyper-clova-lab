"""Read-only deterministic source inventory generation."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import override


@dataclass(frozen=True, slots=True)
class InventoryError(ValueError):
    """Typed source inventory boundary failure."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        """Render the failing path and safe reason."""
        return f"cannot inventory {self.path}: {self.reason}"


class InventoryEntry(BaseModel):
    """Content identity and size for one source file."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    relative_path: str
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class SourceInventory(BaseModel):
    """Deterministic aggregate identity for a source tree."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    root: Path
    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    files: tuple[InventoryEntry, ...]


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(root: Path) -> SourceInventory:
    """Hash every regular file beneath root without modifying source metadata."""
    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise InventoryError(path=root, reason="root is not a directory")

    paths = sorted(resolved_root.rglob("*"), key=lambda path: path.as_posix())
    if any(path.is_symlink() for path in paths):
        symlink = next(path for path in paths if path.is_symlink())
        raise InventoryError(path=symlink, reason="symbolic links are not allowed")
    files = tuple(path for path in paths if path.is_file())
    entries = tuple(
        InventoryEntry(
            relative_path=path.relative_to(resolved_root).as_posix(),
            size_bytes=path.stat().st_size,
            sha256=_file_sha256(path),
        )
        for path in files
    )
    manifest_digest = hashlib.sha256()
    for entry in entries:
        manifest_digest.update(entry.relative_path.encode())
        manifest_digest.update(b"\0")
        manifest_digest.update(entry.sha256.encode())
        manifest_digest.update(b"\0")
        manifest_digest.update(str(entry.size_bytes).encode())
        manifest_digest.update(b"\n")
    return SourceInventory(
        root=resolved_root,
        file_count=len(entries),
        total_bytes=sum(entry.size_bytes for entry in entries),
        sha256=manifest_digest.hexdigest(),
        files=entries,
    )
