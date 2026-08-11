"""Raw-byte-exact OpenAI-compatible model discovery."""

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.discovery.docs_registry import DocumentedModel
from hcx_eval.registry.models import LiveModel, merge_model_registry
from hcx_eval.schemas.model import ModelRecord


class DiscoveryResult(BaseModel):
    """Merged registry plus the observed dispatch count."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    models: tuple[ModelRecord, ...]
    raw_models_path: Path
    external_requests: int


def _write_raw(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        _ = stream.write(raw)


async def discover_models(
    *,
    client: OpenAICompatibleClient,
    documented: tuple[DocumentedModel, ...],
    raw_output: Path,
) -> DiscoveryResult:
    """Fetch once, persist bytes unchanged, and merge the dynamic registry."""

    def preserve(raw: bytes) -> None:
        _write_raw(raw_output, raw)

    raw = await client.fetch_models_raw(preserve)
    response = client.parse_models(raw)
    live = tuple(LiveModel(identifier=identifier) for identifier in response.models)
    return DiscoveryResult(
        models=merge_model_registry(documented, live),
        raw_models_path=raw_output,
        external_requests=1,
    )
