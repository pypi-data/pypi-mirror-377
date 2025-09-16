from ..kernels import patch_loss_functions as patch_loss_functions, post_patch_loss_function as post_patch_loss_function
from ._utils import HAS_FLASH_ATTENTION as HAS_FLASH_ATTENTION, HAS_FLASH_ATTENTION_SOFTCAPPING as HAS_FLASH_ATTENTION_SOFTCAPPING, USE_MODELSCOPE as USE_MODELSCOPE, get_transformers_model_type as get_transformers_model_type, is_bfloat16_supported as is_bfloat16_supported, is_vLLM_available as is_vLLM_available, patch_compiled_autograd as patch_compiled_autograd, patch_compiling_bitsandbytes as patch_compiling_bitsandbytes, patch_model_and_tokenizer as patch_model_and_tokenizer, patch_unsloth_smart_gradient_checkpointing as patch_unsloth_smart_gradient_checkpointing, prepare_model_for_kbit_training as prepare_model_for_kbit_training, process_vision_info as process_vision_info, unsloth_compile_transformers as unsloth_compile_transformers
from .cohere import FastCohereModel as FastCohereModel
from .falcon_h1 import FastFalconH1Model as FastFalconH1Model
from .gemma import FastGemmaModel as FastGemmaModel
from .gemma2 import FastGemma2Model as FastGemma2Model
from .granite import FastGraniteModel as FastGraniteModel
from .llama import FastLlamaModel as FastLlamaModel, logger as logger
from .loader_utils import get_model_name as get_model_name
from .mistral import FastMistralModel as FastMistralModel
from .qwen2 import FastQwen2Model as FastQwen2Model
from .qwen3 import FastQwen3Model as FastQwen3Model
from .qwen3_moe import FastQwen3MoeModel as FastQwen3MoeModel
from .vision import FastBaseModel as FastBaseModel
from _typeshed import Incomplete
from transformers import AutoModelForImageTextToText

SUPPORTS_FOURBIT: Incomplete
SUPPORTS_GEMMA: Incomplete
SUPPORTS_GEMMA2: Incomplete
SUPPORTS_LLAMA31: Incomplete
SUPPORTS_LLAMA32: Incomplete
SUPPORTS_GRANITE: Incomplete
SUPPORTS_QWEN3: Incomplete
SUPPORTS_QWEN3_MOE: Incomplete
SUPPORTS_FALCON_H1: Incomplete
SUPPORTS_GEMMA3N: Incomplete
SUPPORTS_GPTOSS: Incomplete
FORCE_FLOAT32: Incomplete

class FastLanguageModel(FastLlamaModel):
    @staticmethod
    def from_pretrained(model_name: str = 'unsloth/Llama-3.2-1B-Instruct', max_seq_length: int = 2048, dtype=None, load_in_4bit: bool = True, load_in_8bit: bool = False, full_finetuning: bool = False, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, trust_remote_code: bool = False, use_gradient_checkpointing: str = 'unsloth', resize_model_vocab=None, revision=None, use_exact_model_name: bool = False, fast_inference: bool = False, gpu_memory_utilization: float = 0.5, float8_kv_cache: bool = False, random_state: int = 3407, max_lora_rank: int = 64, disable_log_stats: bool = True, qat_scheme=None, *args, **kwargs): ...
AutoModelForVision2Seq = AutoModelForImageTextToText
DISABLE_COMPILE_MODEL_NAMES: Incomplete

class FastModel(FastBaseModel):
    @staticmethod
    def from_pretrained(model_name: str = 'unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit', max_seq_length: int = 2048, dtype=None, load_in_4bit: bool = True, load_in_8bit: bool = False, full_finetuning: bool = False, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, trust_remote_code: bool = False, use_gradient_checkpointing: str = 'unsloth', resize_model_vocab=None, revision=None, return_logits: bool = False, fullgraph: bool = True, use_exact_model_name: bool = False, auto_model=None, whisper_language=None, whisper_task=None, unsloth_force_compile: bool = False, qat_scheme=None, *args, **kwargs): ...

class FastVisionModel(FastModel): ...
class FastTextModel(FastModel): ...
