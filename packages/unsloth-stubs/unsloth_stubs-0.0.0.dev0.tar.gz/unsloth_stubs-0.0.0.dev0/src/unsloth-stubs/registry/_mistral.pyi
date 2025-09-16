from _typeshed import Incomplete
from unsloth.registry.registry import ModelInfo as ModelInfo, ModelMeta as ModelMeta, QuantType as QuantType

class MistralSmallModelInfo(ModelInfo):
    @classmethod
    def construct_model_name(cls, base_name, version, size, quant_type, instruct_tag): ...

MistralSmall_2503_Base_Meta: Incomplete
MistralSmall_2503_Instruct_Meta: Incomplete
MistralSmall_2501_Base_Meta: Incomplete
MistralSmall_2501_Instruct_Meta: Incomplete

def register_mistral_small_models(include_original_model: bool = False): ...
def register_mistral_models(include_original_model: bool = False): ...
