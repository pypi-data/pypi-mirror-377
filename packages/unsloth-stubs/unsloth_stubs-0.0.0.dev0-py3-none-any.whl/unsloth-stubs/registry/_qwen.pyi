from _typeshed import Incomplete
from unsloth.registry.registry import ModelInfo as ModelInfo, ModelMeta as ModelMeta, QuantType as QuantType

class QwenModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

class QwenVLModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

class QwenQwQModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

class QwenQVQPreviewModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

Qwen_2_5_Meta: Incomplete
Qwen_2_5_VLMeta: Incomplete
QwenQwQMeta: Incomplete
QwenQVQPreviewMeta: Incomplete

def register_qwen_2_5_models(include_original_model: bool = False): ...
def register_qwen_2_5_vl_models(include_original_model: bool = False): ...
def register_qwen_qwq_models(include_original_model: bool = False): ...
def register_qwen_models(include_original_model: bool = False): ...
