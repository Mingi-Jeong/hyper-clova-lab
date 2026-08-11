"""Validated offline-first harness configuration."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Self

import yaml
from pydantic import Field, JsonValue, SecretStr, TypeAdapter, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import override

_YAML_MAPPING: Final = TypeAdapter(dict[str, JsonValue])
_ENV_FIELDS: Final = {
    "CLOVA_STUDIO_API_KEY": "clova_studio_api_key",
    "CLOVA_STUDIO_BASE_URL": "clova_studio_base_url",
    "CLOVA_OPENAI_BASE_URL": "clova_openai_base_url",
    "DATA_ROOT": "data_root",
    "NAVER_DOCS_ROOT": "naver_docs_root",
    "RESULTS_ROOT": "results_root",
    "REQUEST_TIMEOUT_SECONDS": "request_timeout_seconds",
    "MAX_CONCURRENCY": "max_concurrency",
    "MAX_REQUESTS_PER_RUN": "max_requests_per_run",
    "MAX_TOKENS_PER_RUN": "max_tokens_per_run",
    "MAX_ESTIMATED_COST_KRW": "max_estimated_cost_krw",
    "EXECUTE": "execute",
}


@dataclass(frozen=True, slots=True)
class ConfigLoadError(ValueError):
    """Typed configuration-file boundary failure."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        """Render a safe error without source contents."""
        return f"cannot load configuration {self.path}: {self.reason}"


class HarnessSettings(BaseSettings):
    """Configuration that cannot enable network execution accidentally."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        frozen=True,
    )

    clova_studio_api_key: SecretStr | None = None
    clova_studio_base_url: str = "https://clovastudio.stream.ntruss.com"
    clova_openai_base_url: str = "https://clovastudio.stream.ntruss.com/v1/openai"
    data_root: Path = Path("processed-data")
    naver_docs_root: Path = Path("naver-clova-studio-instructions-all-docs")
    results_root: Path = Path("results")
    request_timeout_seconds: float = Field(default=120, gt=0)
    max_concurrency: int = Field(default=5, gt=0)
    max_requests_per_run: int = Field(default=0, ge=0)
    max_tokens_per_run: int = Field(default=0, ge=0)
    max_estimated_cost_krw: int = Field(default=0, ge=0)
    execute: bool = False

    @model_validator(mode="after")
    def validate_execution_contract(self) -> Self:
        """Require explicit credentials and bounded live execution."""
        if self.execute and self.clova_studio_api_key is None:
            message = "execution requires an API key"
            raise ValueError(message)
        if self.execute and self.max_requests_per_run <= 0:
            message = "execution requires a positive request budget"
            raise ValueError(message)
        if self.execute and self.max_tokens_per_run <= 0:
            message = "execution requires a positive token budget"
            raise ValueError(message)
        return self


def load_settings(path: Path) -> HarnessSettings:
    """Load a YAML overlay with environment variables taking precedence."""
    try:
        values = _YAML_MAPPING.validate_python(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
        raise ConfigLoadError(path=path, reason=str(error)) from error

    for field in ("data_root", "naver_docs_root", "results_root"):
        candidate = values.get(field)
        if isinstance(candidate, str):
            candidate_path = Path(candidate)
            values[field] = str(
                candidate_path
                if candidate_path.is_absolute()
                else (path.parent / candidate_path).resolve()
            )

    for environment_name, field_name in _ENV_FIELDS.items():
        environment_value = os.environ.get(environment_name)
        if environment_value is not None:
            values[field_name] = environment_value
    return HarnessSettings.model_validate(values)
