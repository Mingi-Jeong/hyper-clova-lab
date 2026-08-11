"""Evidence-preserving merge of official documentation and live models."""

from collections.abc import Iterable
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from hcx_eval.discovery.docs_registry import DocumentedModel
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus

_NO_IDS = frozenset[str]()


class LiveModel(BaseModel):
    """Normalized model entry from the live `/models` snapshot."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    identifier: str
    status: ModelStatus = ModelStatus.LIVE
    capabilities: tuple[str, ...] = ()


def _document_capabilities(model: DocumentedModel | None) -> dict[str, set[str]]:
    if model is None:
        return {}
    evidence = (
        f"official-docs:{','.join(str(value) for value in model.evidence_document_ids)}"
    )
    return {name: {evidence} for name in model.capabilities}


def _model_status(
    identifier: str,
    live_model: LiveModel | None,
    deprecated_ids: frozenset[str],
    restricted_ids: frozenset[str],
) -> ModelStatus:
    if live_model is not None:
        return (
            ModelStatus.RESTRICTED
            if identifier in restricted_ids
            else live_model.status
        )
    return (
        ModelStatus.DEPRECATED
        if identifier in deprecated_ids
        else ModelStatus.UNAVAILABLE
    )


def merge_model_registry(
    documented: Iterable[DocumentedModel],
    live: Iterable[LiveModel],
    *,
    deprecated_ids: frozenset[str] = _NO_IDS,
    restricted_ids: frozenset[str] = _NO_IDS,
) -> tuple[ModelRecord, ...]:
    """Merge all sources without dropping documentary or live-only identifiers."""
    documented_by_id = {model.identifier: model for model in documented}
    live_by_id: dict[str, LiveModel] = {}
    for model in live:
        previous = live_by_id.get(model.identifier)
        capabilities = set(model.capabilities)
        if previous is not None:
            capabilities.update(previous.capabilities)
        live_by_id[model.identifier] = model.model_copy(
            update={"capabilities": tuple(sorted(capabilities))}
        )

    records: list[ModelRecord] = []
    for identifier in sorted(documented_by_id.keys() | live_by_id.keys()):
        documented_model = documented_by_id.get(identifier)
        live_model = live_by_id.get(identifier)
        capability_evidence = _document_capabilities(documented_model)
        if live_model is not None:
            for name in live_model.capabilities:
                capability_evidence.setdefault(name, set()).add("live:/models")

        status = _model_status(identifier, live_model, deprecated_ids, restricted_ids)

        evidence: list[str] = []
        if documented_model is not None:
            evidence.extend(
                f"official-docs:{value}"
                for value in documented_model.evidence_document_ids
            )
        if identifier in deprecated_ids:
            evidence.append("official-docs:deprecated")
        if live_model is not None:
            evidence.append("live:/models")
        capabilities = tuple(
            Capability(
                name=name,
                supported=True if "official-docs" in "".join(sources) else None,
                evidence=tuple(sorted(sources)),
            )
            for name, sources in sorted(capability_evidence.items())
        )
        records.append(
            ModelRecord(
                identifier=identifier,
                status=status,
                endpoints=()
                if documented_model is None
                else documented_model.endpoints,
                capabilities=capabilities,
                evidence=tuple(evidence),
            )
        )
    return tuple(records)
