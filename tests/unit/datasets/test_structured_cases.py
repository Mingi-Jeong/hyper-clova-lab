from __future__ import annotations

from pathlib import Path

import pytest

from hcx_eval.datasets.cases import (
    CaseOutputConflictError,
    build_structured_cases,
    write_case_bundle,
)
from hcx_eval.datasets.faq import DatasetFormatError, load_faq_records
from hcx_eval.datasets.transfer_codes import load_transfer_reasons

_FAQ_HEADER = "ID,카테고리,대표질문,유사질문표현,표준답변,AI분기포인트,근거구분,근거ID"


def _write_lines(path: Path, lines: tuple[str, ...]) -> None:
    _ = path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_builds_all_structured_cases_deterministically_without_source_writes() -> None:
    # Given: the protected structured source package and its initial file metadata.
    data_root = Path("processed-data")
    source_paths = tuple(sorted((data_root / "datasets").glob("*.csv")))
    before = tuple(
        (path, path.stat().st_mtime_ns, path.read_bytes()) for path in source_paths
    )

    # When: the case set is built twice.
    first = build_structured_cases(data_root)
    second = build_structured_cases(data_root)

    # Then: IDs, ordering, splits, and serialized content are stable.
    assert first == second
    assert len(first.cases) == 352
    assert len({case.case_id for case in first.cases}) == 352
    assert {case.task for case in first.cases} == {
        "default_option_qa",
        "transfer_code_to_reason",
        "transfer_reason_to_code",
    }
    assert all(case.dataset_sha256 == first.dataset_sha256 for case in first.cases)

    faq_one = tuple(
        case for case in first.cases if case.case_id.startswith("FAQ-0001-")
    )
    assert len(faq_one) == 3
    assert {case.metadata["split"].value for case in faq_one} <= {
        "development",
        "validation",
        "test",
    }
    assert len({case.metadata["split"].value for case in faq_one}) == 1
    assert (
        sum(case.metadata["review_status"].value == "unreviewed" for case in faq_one)
        == 2
    )

    after = tuple(
        (path, path.stat().st_mtime_ns, path.read_bytes()) for path in source_paths
    )
    assert after == before


def test_faq_loader_rejects_missing_columns_duplicate_ids_and_bad_encoding(
    tmp_path: Path,
) -> None:
    # Given: a valid source registry and malformed FAQ variants.
    sources = tmp_path / "sources.csv"
    _write_lines(
        sources,
        ("SourceID,설명,URL,비고", "S1,source,https://offline.invalid,none"),
    )
    missing = tmp_path / "missing.csv"
    _write_lines(missing, ("ID,대표질문", "1,question"))
    duplicate = tmp_path / "duplicate.csv"
    _write_lines(
        duplicate,
        (
            _FAQ_HEADER,
            "1,category,question,one / two,answer,fact,kind,S1",
            "1,category,question,one / two,answer,fact,kind,S1",
        ),
    )
    invalid = tmp_path / "invalid.csv"
    _ = invalid.write_bytes(b"\xff\xfe")

    # When / Then: every malformed boundary fails explicitly.
    with pytest.raises(DatasetFormatError, match="missing required columns"):
        _ = load_faq_records(missing, sources)
    with pytest.raises(DatasetFormatError, match="duplicate ID"):
        _ = load_faq_records(duplicate, sources)
    with pytest.raises(DatasetFormatError, match="UTF-8"):
        _ = load_faq_records(invalid, sources)


def test_loaders_reject_unknown_sources_and_duplicate_transfer_codes(
    tmp_path: Path,
) -> None:
    # Given: an FAQ with an unknown citation and repeated transfer code.
    sources = tmp_path / "sources.csv"
    _write_lines(
        sources,
        ("SourceID,설명,URL,비고", "S1,source,https://offline.invalid,none"),
    )
    faq = tmp_path / "faq.csv"
    _write_lines(
        faq,
        (_FAQ_HEADER, "1,category,question,one / two,answer,fact,kind,S2"),
    )
    transfer = tmp_path / "transfer.csv"
    _write_lines(
        transfer,
        (
            "code,reason_name,description",
            "01,reason,description",
            "01,reason,description",
        ),
    )

    # When / Then: cross-file references and duplicate codes are validated.
    with pytest.raises(DatasetFormatError, match="unknown source IDs"):
        _ = load_faq_records(faq, sources)
    with pytest.raises(DatasetFormatError, match="duplicate code"):
        _ = load_transfer_reasons(transfer)


def test_case_bundle_writer_is_idempotent_and_never_overwrites(
    tmp_path: Path,
) -> None:
    # Given: one deterministic structured bundle.
    bundle = build_structured_cases(Path("processed-data"))
    output = tmp_path / "structured.jsonl"

    # When: the same bundle is written repeatedly.
    first = write_case_bundle(bundle, output)
    second = write_case_bundle(bundle, output)

    # Then: bytes and inventory remain stable, while divergent content is rejected.
    assert first == second
    assert first.case_count == 352
    assert first.sha256 == bundle.cases_sha256
    changed = bundle.model_copy(update={"cases": bundle.cases[:-1]})
    with pytest.raises(CaseOutputConflictError):
        _ = write_case_bundle(changed, output)
