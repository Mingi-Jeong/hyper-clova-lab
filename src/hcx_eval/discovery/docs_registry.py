"""Official documentation snapshot parser and traceable model registry."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing_extensions import override

from hcx_eval.schemas.model import ModelStatus

_MODEL_IDENTIFIERS: Final = (
    r"HCX(?:-DASH)?-\d{3}|LK-(?:B|D2)|bge-m3|clir-(?:emb|sts)-dolphin"
)
_MODEL_PATTERN: Final = re.compile(
    rf"(?<!\w)(?:{_MODEL_IDENTIFIERS})(?!\w)",
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
    status_hint: ModelStatus = ModelStatus.DOCUMENTED


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


def _snapshot_status(
    documents: tuple[SnapshotDocument, ...],
) -> ModelStatus:
    historical_example = all(
        document.section == "튜닝" and "목록 조회" in document.title
        for document in documents
    )
    return (
        ModelStatus.HISTORICAL_EXAMPLE_ONLY
        if historical_example
        else ModelStatus.DOCUMENTED
    )


def _normalize_identifier(identifier: str) -> str:
    folded = identifier.casefold()
    return identifier.upper() if folded.startswith(("hcx", "lk-")) else folded


def _catalog_status(line: str) -> ModelStatus:
    folded = line.casefold()
    if "교체" in folded or "deprecated" in folded:
        return ModelStatus.DEPRECATED
    if "과거" in folded or "historical" in folded:
        return ModelStatus.HISTORICAL_EXAMPLE_ONLY
    return ModelStatus.DOCUMENTED


def _merge_catalog_models(
    models: list[DocumentedModel], catalog_path: Path
) -> list[DocumentedModel]:
    try:
        catalog = catalog_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise DocsSnapshotError(path=catalog_path, reason=str(error)) from error
    evidence_url = f"urn:local-doc:{catalog_path.name}"
    catalog_statuses: dict[str, ModelStatus] = {}
    for line in catalog.splitlines():
        for match in _MODEL_PATTERN.finditer(line):
            identifier = _normalize_identifier(match.group(0))
            status = _catalog_status(line)
            previous = catalog_statuses.get(identifier, ModelStatus.DOCUMENTED)
            if previous is ModelStatus.DOCUMENTED or status is ModelStatus.DEPRECATED:
                catalog_statuses[identifier] = status

    by_id = {model.identifier: model for model in models}
    for identifier, status in catalog_statuses.items():
        existing = by_id.get(identifier)
        if existing is None:
            by_id[identifier] = DocumentedModel(
                identifier=identifier,
                capabilities=(),
                endpoints=(),
                evidence_document_ids=(),
                evidence_urls=(evidence_url,),
                status_hint=status,
            )
        else:
            by_id[identifier] = existing.model_copy(
                update={
                    "evidence_urls": tuple(
                        sorted({*existing.evidence_urls, evidence_url})
                    ),
                    "status_hint": status,
                }
            )
    return [by_id[identifier] for identifier in sorted(by_id)]


def parse_docs_snapshot(
    path: Path, *, catalog_path: Path | None = None
) -> DocsRegistry:
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
            identifier = _normalize_identifier(match.group(0))
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
                status_hint=_snapshot_status(documents),
            )
        )
    if catalog_path is not None:
        models = _merge_catalog_models(models, catalog_path)
    return DocsRegistry(
        snapshot_sha256=hashlib.sha256(raw).hexdigest(),
        documents=envelope.documents,
        models=tuple(models),
    )
