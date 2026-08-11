from hcx_eval.discovery.docs_registry import DocumentedModel
from hcx_eval.registry.models import LiveModel, merge_model_registry
from hcx_eval.schemas.model import ModelStatus


def documented(identifier: str, capabilities: tuple[str, ...] = ()) -> DocumentedModel:
    return DocumentedModel(
        identifier=identifier,
        capabilities=capabilities,
        endpoints=("/v3/chat-completions/{modelName}",),
        evidence_document_ids=(2,),
        evidence_urls=("https://docs.invalid/model",),
    )


def test_registry_merge_keeps_documented_only_live_only_and_provenance() -> None:
    # Given
    docs = (documented("DOC-ONLY", ("generation",)), documented("BOTH", ("vision",)))
    live = (
        LiveModel(identifier="LIVE-ONLY"),
        LiveModel(identifier="BOTH", capabilities=("generation",)),
    )

    # When
    merged = merge_model_registry(docs, live)

    # Then
    by_id = {record.identifier: record for record in merged}
    assert by_id["DOC-ONLY"].status is ModelStatus.UNAVAILABLE
    assert by_id["LIVE-ONLY"].status is ModelStatus.LIVE
    assert by_id["BOTH"].status is ModelStatus.LIVE
    capability = {item.name: item for item in by_id["BOTH"].capabilities}
    assert capability["vision"].evidence == ("official-docs:2",)
    assert capability["generation"].evidence == ("live:/models",)


def test_registry_merge_marks_documented_deprecation_but_live_conflict_as_live() -> (
    None
):
    # Given
    docs = (documented("OLD"),)
    live = (LiveModel(identifier="OLD"),)

    # When
    merged = merge_model_registry(docs, live, deprecated_ids=frozenset({"OLD"}))

    # Then
    assert merged[0].status is ModelStatus.LIVE
    assert "official-docs:deprecated" in merged[0].evidence


def test_registry_merge_deduplicates_live_ids_and_preserves_unknown_capability() -> (
    None
):
    # Given
    live = (
        LiveModel(identifier="NEW", capabilities=("future_mode",)),
        LiveModel(identifier="NEW"),
    )

    # When
    merged = merge_model_registry((), live)

    # Then
    assert len(merged) == 1
    assert merged[0].capabilities[0].name == "future_mode"
    assert merged[0].capabilities[0].supported is None
