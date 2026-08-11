from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from hcx_eval.discovery.docs_registry import DocsSnapshotError, parse_docs_snapshot
from hcx_eval.schemas.model import ModelStatus

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_official_snapshot_registers_all_documents_and_documented_models() -> None:
    # Given: the immutable collected official snapshot.
    snapshot = Path(
        "naver-clova-studio-instructions-all-docs/naver_clova_studio_all_docs.json"
    )

    # When: the registry is parsed.
    registry = parse_docs_snapshot(
        snapshot,
        catalog_path=Path("docs/model-evaluation/02_HYPERCLOVA_MODEL_CATALOG.md"),
    )

    # Then: all documents and the full documented model set are traceable.
    assert len(registry.documents) == 31
    assert {model.identifier for model in registry.models} == {
        "HCX-002",
        "HCX-003",
        "HCX-005",
        "HCX-007",
        "HCX-DASH-001",
        "HCX-DASH-002",
        "bge-m3",
        "clir-emb-dolphin",
        "clir-sts-dolphin",
        "LK-B",
        "LK-D2",
    }
    assert all(
        model.evidence_document_ids or model.evidence_urls for model in registry.models
    )
    by_id = {model.identifier: model for model in registry.models}
    assert by_id["HCX-002"].status_hint is ModelStatus.HISTORICAL_EXAMPLE_ONLY
    assert by_id["LK-B"].status_hint is ModelStatus.DEPRECATED
    assert by_id["LK-D2"].status_hint is ModelStatus.DEPRECATED


def test_snapshot_provenance_marks_task_example_as_historical() -> None:
    # Given
    snapshot = Path(
        "naver-clova-studio-instructions-all-docs/naver_clova_studio_all_docs.json"
    )

    # When
    registry = parse_docs_snapshot(snapshot)

    # Then
    by_id = {model.identifier: model for model in registry.models}
    assert by_id["HCX-002"].status_hint is ModelStatus.HISTORICAL_EXAMPLE_ONLY


def test_snapshot_parser_rejects_duplicate_document_ids(tmp_path: Path) -> None:
    # Given: two documents claiming the same source identity.
    document: dict[str, JsonValue] = {
        "id": 1,
        "section": "section",
        "title": "title",
        "source_label": "source",
        "url": "https://example.test/doc",
        "headings": [],
        "content": "HCX-005 /v3/chat-completions/{modelName}",
    }
    snapshot: dict[str, JsonValue] = {
        "dataset": "test",
        "source": "test",
        "scope": "test",
        "collected_at": "2026-01-01T00:00:00Z",
        "section_count": 1,
        "document_count": 2,
        "sections": [{"section": "section", "document_count": 2}],
        "documents": [document, document],
    }
    path = tmp_path / "snapshot.json"
    _ = path.write_text(json.dumps(snapshot), encoding="utf-8")

    # When / Then: duplicate traceability keys are rejected.
    with pytest.raises(DocsSnapshotError):
        _ = parse_docs_snapshot(path)


def test_snapshot_parser_rejects_malformed_json(tmp_path: Path) -> None:
    # Given: truncated JSON input.
    path = tmp_path / "snapshot.json"
    _ = path.write_text('{"documents":', encoding="utf-8")

    # When / Then: a typed source error is raised.
    with pytest.raises(DocsSnapshotError):
        _ = parse_docs_snapshot(path)
