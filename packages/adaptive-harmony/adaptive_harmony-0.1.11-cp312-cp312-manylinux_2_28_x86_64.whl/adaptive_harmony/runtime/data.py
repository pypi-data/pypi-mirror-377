from adaptive_harmony.adaptive_harmony import HarmonyClient, ModelBuilder
from pydantic import BaseModel
import json
import re
from typing import Self


class InputConfig(BaseModel):
    @classmethod
    def load_from_file(cls, json_file) -> Self:
        with open(json_file, "r") as f:
            data = json.load(f)
        return cls.model_validate(data)


from .dto.AdaptiveDataset import AdaptiveDataset as AdaptiveDataset
from .dto.AdaptiveGrader import (
    AdaptiveGrader as DtoGrader,
    Judge as CustomJudge,
    Prebuilt as PrebuiltJudge,
    Remote as RemoteRewardEndpoint,
    PrebuiltConfigKey,
    JudgeExample as CustomJudgeExample,
)
from .dto.AdaptiveModel import AdaptiveModel as DtoModel

__all__ = [
    "InputConfig",
    "AdaptiveDataset",
    "AdaptiveModel",
    "AdaptiveGrader",
    "CustomJudge",
    "CustomJudgeExample",
    "PrebuiltJudge",
    "PrebuiltConfigKey",
    "RemoteRewardEndpoint",
]


# Patches for generated dto objects
class AdaptiveModel(DtoModel):

    def to_builder(
        self,
        client: HarmonyClient,
        kv_cache_len: int | None = None,
        tokens_to_generate: int | None = None,
        tp: int | None = None,
    ) -> ModelBuilder:
        """
        Create a ModelBuilder instance configured with this model's parameters.
        Applies configuration from both the model's stored parameters and any override parameters
        provided as arguments. Override parameters take precedence over stored parameters.

        Args:
            client (HarmonyClient): The client instance used to create the model builder
            kv_cache_len (int | None, optional)
            tokens_to_generate (int | None, optional)
            tp (int | None, optional)

        Returns:
            ModelBuilder: A configured model builder instance ready for use

        Note:
            The method maps self.params.max_seq_len to the tokens_to_generate parameter
            in the builder configuration.
        """
        kwargs = {}
        if self.params:
            if self.params.kv_cache_len is not None:
                kwargs["kv_cache_len"] = self.params.kv_cache_len
            if self.params.max_seq_len is not None:
                kwargs["tokens_to_generate"] = self.params.max_seq_len

        if kv_cache_len:
            kwargs["kv_cache_len"] = kv_cache_len
        if tokens_to_generate:
            kwargs["tokens_to_generate"] = tokens_to_generate
        builder = client.model(self.path, **kwargs)
        if self.params and self.params.tp:
            builder = builder.tp(self.params.tp)
        if tp:
            builder = builder.tp(tp)
        return builder

    def __repr__(self) -> str:
        # Redact api_key in the path if present, show only last 3 chars
        def redact_api_key(match):
            key = match.group(2)
            if len(key) > 3:
                redacted = "<REDACTED>" + key[-3:]
            else:
                redacted = "<REDACTED>"
            return f"{match.group(1)}{redacted}"

        redacted_path = re.sub(r"(api_key=)([^&]+)", redact_api_key, self.path)
        return f"AdaptiveModel(path='{redacted_path}')"

    def __hash__(self) -> int:
        return hash(self.path) + hash(self.model_key)


class AdaptiveGrader(DtoGrader):
    def __hash__(self) -> int:
        return hash(self.grader_id)
