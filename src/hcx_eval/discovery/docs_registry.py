"""Official documentation snapshot parser and traceable model registry."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing_extensions import override

_MODEL_PATTERN: Final = re.compile(
    r"(?<!\w)(?:HCX(?:-DASH)?-\d{3}|bge-m3|clir-(?:emb|sts)-dolphin)(?!\w)",
    re.IGNORECASE,
)
_ENDPOINT_PATTERN: Final = re.compile(r"(?<!:)\/(?:v\d+\/)?[a-z][A-Za-z0-9_{}./-]+")


@dataclass(frozen=True, slots=True)
class DocsSnapshotError(ValueError):
    """Typed official-snapshot parsing failure."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        """Render the failing snapshot path and safe reason."""
        return f"cannot parse documentation snapshot {self.path}: {self.reason}"


class SnapshotDocument(BaseModel):
    """One immutable document from the collected official source."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int = Field(gt=0)
    section: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    headings: tuple[str, ...]
    content: str


class SnapshotEnvelope(BaseModel):
    """Validated top-level official snapshot metadata and documents."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    dataset: str
    source: str
    scope: str
    collected_at: str
    section_count: int = Field(gt=0)
    document_count: int = Field(gt=0)
    documents: tuple[SnapshotDocument, ...]


class DocumentedModel(BaseModel):
    """Document-derived model with capability and endpoint evidence."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    identifier: str
    capabilities: tuple[str, ...]
    endpoints: tuple[str, ...]
    evidence_document_ids: tuple[int, ...]
    evidence_urls: tuple[str, ...]


class DocsRegistry(BaseModel):
    """Complete traceable registry parsed from an official snapshot."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    documents: tuple[SnapshotDocument, ...]
    models: tuple[DocumentedModel, ...]


def _capabilities(document: SnapshotDocument) -> set[str]:
    text = f"{document.section}\n{document.title}\n{document.content}".casefold()
    capabilities: set[str] = set()
    terms = {
        "embedding": ("임베딩", "embedding"),
        "function_calling": ("function calling",),
        "generation": ("chat completions",),
        "structured_outputs": ("structured outputs",),
        "thinking": ("thinking", "추론"),
        "vision": ("이미지", "vision"),
    }
    for capability, needles in terms.items():
        if any(needle in text for needle in needles):
            capabilities.add(capability)
    return capabilities


def parse_docs_snapshot(path: Path) -> DocsRegistry:
    """Parse the collected JSON snapshot into a model-to-document registry."""
    try:
        raw = path.read_bytes()
        envelope = SnapshotEnvelope.model_validate_json(raw)
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise DocsSnapshotError(path=path, reason=str(error)) from error
    if len(envelope.documents) != envelope.document_count:
        raise DocsSnapshotError(path=path, reason="document count mismatch")
    document_ids = [document.id for document in envelope.documents]
    if len(document_ids) != len(set(document_ids)):
        raise DocsSnapshotError(path=path, reason="duplicate document id")

    model_evidence: dict[str, list[SnapshotDocument]] = {}
    for document in envelope.documents:
        document_text = "\n".join(
            (document.title, *document.headings, document.content)
        )
        for match in _MODEL_PATTERN.finditer(document_text):
            identifier = match.group(0)
            if identifier.casefold().startswith("hcx"):
                identifier = identifier.upper()
            else:
                identifier = identifier.lower()
            model_evidence.setdefault(identifier, []).append(document)

    models: list[DocumentedModel] = []
    for identifier, evidence in sorted(model_evidence.items()):
        unique_documents = {document.id: document for document in evidence}
        documents = tuple(unique_documents[key] for key in sorted(unique_documents))
        endpoints = sorted(
            {
                match.group(0)
                for document in documents
                for match in _ENDPOINT_PATTERN.finditer(document.content)
            }
        )
        models.append(
            DocumentedModel(
                identifier=identifier,
                capabilities=tuple(
                    sorted(
                        capability
                        for document in documents
                        for capability in _capabilities(document)
                    )
                ),
                endpoints=tuple(endpoints),
                evidence_document_ids=tuple(document.id for document in documents),
                evidence_urls=tuple(document.url for document in documents),
            )
        )
    return DocsRegistry(
        snapshot_sha256=hashlib.sha256(raw).hexdigest(),
        documents=envelope.documents,
        models=tuple(models),
    )
