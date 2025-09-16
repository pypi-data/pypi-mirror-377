from _typeshed import Incomplete
from unsloth.registry.registry import ModelInfo as ModelInfo, ModelMeta as ModelMeta, QuantType as QuantType

class LlamaModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

class LlamaVisionModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

LlamaMeta_3_1: Incomplete
LlamaMeta_3_2_Base: Incomplete
LlamaMeta_3_2_Instruct: Incomplete
LlamaMeta_3_2_Vision: Incomplete

def register_llama_3_1_models(include_original_model: bool = False): ...
def register_llama_3_2_models(include_original_model: bool = False): ...
def register_llama_3_2_vision_models(include_original_model: bool = False): ...
def register_llama_models(include_original_model: bool = False): ...
