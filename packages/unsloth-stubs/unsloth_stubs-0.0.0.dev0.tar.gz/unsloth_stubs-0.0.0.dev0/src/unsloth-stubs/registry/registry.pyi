from _typeshed import Incomplete
from dataclasses import dataclass, field
from enum import Enum

class QuantType(Enum):
    BNB = 'bnb'
    UNSLOTH = 'unsloth'
    GGUF = 'GGUF'
    NONE = 'none'
    BF16 = 'bf16'

BNB_QUANTIZED_TAG: str
UNSLOTH_DYNAMIC_QUANT_TAG: Incomplete
GGUF_TAG: str
BF16_TAG: str
QUANT_TAG_MAP: Incomplete

@dataclass
class ModelInfo:
    org: str
    base_name: str
    version: str
    size: int
    name: str = ...
    is_multimodal: bool = ...
    instruct_tag: str = ...
    quant_type: QuantType = ...
    description: str = ...
    def __post_init__(self) -> None: ...
    @staticmethod
    def append_instruct_tag(key: str, instruct_tag: str = None): ...
    @staticmethod
    def append_quant_type(key: str, quant_type: QuantType = None): ...
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag, key: str = ''): ...
    @property
    def model_path(self) -> str: ...

@dataclass
class ModelMeta:
    org: str
    base_name: str
    model_version: str
    model_info_cls: type[ModelInfo]
    model_sizes: list[str] = field(default_factory=list)
    instruct_tags: list[str] = field(default_factory=list)
    quant_types: list[QuantType] | dict[str, list[QuantType]] = field(default_factory=list)
    is_multimodal: bool = ...

MODEL_REGISTRY: dict[str, ModelInfo]

def register_model(model_info_cls: ModelInfo, org: str, base_name: str, version: str, size: int, instruct_tag: str = None, quant_type: QuantType = None, is_multimodal: bool = False, name: str = None): ...
