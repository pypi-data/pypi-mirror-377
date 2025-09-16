from ._utils import *
from ..kernels import *
from ..tokenizer_utils import *
import torch
from ..save import patch_saving_functions as patch_saving_functions
from ._utils import __version__ as __version__, importlib_version as importlib_version, move_to_device as move_to_device, patch_unsloth_smart_gradient_checkpointing as patch_unsloth_smart_gradient_checkpointing
from .rl import PatchFastRL as PatchFastRL
from .vision import FastBaseModel as FastBaseModel
from _typeshed import Incomplete
from transformers import AutoTokenizer as AutoTokenizer
from transformers.models.llama.modeling_llama import BaseModelOutputWithPast, LlamaAttention
from unsloth import DEVICE_COUNT as DEVICE_COUNT, DEVICE_TYPE as DEVICE_TYPE

IS_ATTENTION_REFACTOR: Incomplete
LlamaSdpaAttention = LlamaAttention
LlamaFlashAttention2 = LlamaAttention
HAS_XFORMERS: Incomplete
BlockDiagonalCausalMask: Incomplete
clean_gpu_cache: Incomplete
get_current_device: Incomplete

def original_apply_qkv(self, X): ...
def original_apply_o(self, X): ...

KV_CACHE_INCREMENT: int
torch_nn_functional_softmax: Incomplete
SDPA_HAS_GQA: Incomplete

def fix_prepare_inputs_for_generation(module) -> None: ...

torch_matmul: Incomplete

def LlamaAttention_fast_forward_inference(self, hidden_states: torch.Tensor, past_key_value: tuple[torch.Tensor] | None, position_ids, do_prefill: bool = False, attention_mask=None): ...

torch_nn_functional_silu: Incomplete

def fast_swiglu_inference(self, X, temp_gate=None, temp_up=None, gate_multiplier=None, down_multiplier=None): ...

torch_square: Incomplete
torch_mean: Incomplete

def fast_rms_layernorm_inference(self, X, XX=None, XX2=None, variance=None): ...
def fast_rms_layernorm_inference_gemma(self, X, out_weight=None): ...
def fast_layernorm_compiled(layernorm, X): ...
def LlamaAttention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: BlockDiagonalCausalMask | None = None, attention_mask: torch.Tensor | None = None, position_ids: torch.LongTensor | None = None, past_key_value: tuple[torch.Tensor] | None = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: torch.LongTensor | None = None, position_embeddings: tuple[torch.Tensor, torch.Tensor] | None = None, *args, **kwargs) -> tuple[torch.Tensor, torch.Tensor | None, tuple[torch.Tensor] | None]: ...
def LlamaDecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask=None, attention_mask: torch.Tensor | None = None, position_ids: torch.LongTensor | None = None, past_key_value: tuple[torch.Tensor] | None = None, output_attentions: bool | None = False, use_cache: bool | None = False, padding_mask: torch.LongTensor | None = None, position_embeddings: tuple[torch.Tensor, torch.Tensor] | None = None, *args, **kwargs) -> tuple[torch.FloatTensor, tuple[torch.FloatTensor, torch.FloatTensor] | None]: ...
def LlamaModel_fast_forward(self, input_ids: torch.LongTensor, causal_mask: BlockDiagonalCausalMask | None = None, attention_mask: torch.Tensor | None = None, position_ids: torch.LongTensor | None = None, past_key_values: list[torch.FloatTensor] | None = None, inputs_embeds: torch.FloatTensor | None = None, use_cache: bool | None = None, output_attentions: bool | None = None, output_hidden_states: bool | None = None, return_dict: bool | None = None, *args, **kwargs) -> tuple | BaseModelOutputWithPast: ...

LlamaModel_fast_forward_inference: Incomplete

def CausalLM_fast_forward(fast_forward_inference): ...
@torch._disable_dynamo
def PeftModel_fast_forward(self, input_ids=None, causal_mask=None, attention_mask=None, inputs_embeds=None, labels=None, output_attentions=None, output_hidden_states=None, return_dict=None, task_ids=None, num_logits_to_keep: int = 0, logits_to_keep: int = 0, **kwargs): ...

class LlamaRotaryEmbedding(torch.nn.Module):
    dim: Incomplete
    max_position_embeddings: Incomplete
    base: Incomplete
    current_rope_size: Incomplete
    multi_gpu_cos_cached: Incomplete
    multi_gpu_sin_cached: Incomplete
    cos_cached: Incomplete
    sin_cached: Incomplete
    def __init__(self, dim=None, max_position_embeddings: int = 2048, base: int = 10000, device=None, config=None) -> None: ...
    def forward(self, x, position_ids=None, seq_len=None): ...
    def get_cached(self, seq_len=None, device_index=None): ...
    def extend_rope_embedding(self, x, seq_len) -> None: ...

class LlamaLinearScalingRotaryEmbedding(LlamaRotaryEmbedding):
    scaling_factor: Incomplete
    def __init__(self, dim=None, max_position_embeddings: int = 2048, base: int = 10000, device=None, scaling_factor: float = 1.0, config=None) -> None: ...

class LlamaExtendedRotaryEmbedding(torch.nn.Module):
    dim: Incomplete
    max_position_embeddings: Incomplete
    base: Incomplete
    current_rope_size: Incomplete
    multi_gpu_cos_cached: Incomplete
    multi_gpu_sin_cached: Incomplete
    cos_cached: Incomplete
    sin_cached: Incomplete
    def __init__(self, dim=None, max_position_embeddings: int = 2048, base: int = 10000, device=None, config=None) -> None: ...
    def forward(self, x, position_ids=None, seq_len=None): ...
    def get_cached(self, seq_len=None, device_index=None): ...
    def extend_rope_embedding(self, x, seq_len) -> None: ...
    def apply_scaling(self, freqs: torch.Tensor): ...

class LongRopeRotaryEmbedding(torch.nn.Module):
    dim: Incomplete
    max_position_embeddings: Incomplete
    original_max_position_embeddings: Incomplete
    base: Incomplete
    current_rope_size: Incomplete
    multi_gpu_short_cos_cached: Incomplete
    multi_gpu_short_sin_cached: Incomplete
    multi_gpu_long_cos_cached: Incomplete
    multi_gpu_long_sin_cached: Incomplete
    scaling_factor: Incomplete
    short_cos_cached: Incomplete
    short_sin_cached: Incomplete
    long_cos_cached: Incomplete
    long_sin_cached: Incomplete
    def __init__(self, dim=None, max_position_embeddings: int = 131072, original_max_position_embeddings: int = 4096, base: int = 10000, short_factor=None, long_factor=None, device=None, config=None) -> None: ...
    def forward(self, x, position_ids=None, seq_len=None): ...
    def get_cached(self, seq_len=None, device_index=None): ...
    def extend_rope_embedding(self, x, seq_len) -> None: ...

def unsloth_fast_generate(self, *args, **kwargs): ...

class FastLlamaModel:
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def from_pretrained(model_name: str = 'unsloth/llama-3-8b-bnb-4bit', max_seq_length=None, dtype=None, load_in_4bit: bool = True, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, model_patcher=None, tokenizer_name=None, trust_remote_code: bool = False, revision=None, fast_inference: bool = False, gpu_memory_utilization: float = 0.5, float8_kv_cache: bool = False, random_state: int = 3407, max_lora_rank: int = 16, disable_log_stats: bool = False, unsloth_vllm_standby: bool = False, num_labels=None, qat_scheme=None, **kwargs): ...
    @staticmethod
    def post_patch(model, tokenizer): ...
    @staticmethod
    def get_peft_model(model, r: int = 16, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'], lora_alpha: int = 16, lora_dropout: float = 0.0, bias: str = 'none', layers_to_transform=None, layers_pattern=None, use_gradient_checkpointing: str = 'unsloth', random_state: int = 3407, max_seq_length: int = 2048, use_rslora: bool = False, modules_to_save=None, init_lora_weights: bool = True, loftq_config={}, temporary_location: str = '_unsloth_temporary_saved_buffers', qat_scheme=None, **kwargs): ...
    @staticmethod
    def patch_peft_model(model, use_gradient_checkpointing: str = 'unsloth'): ...
    @staticmethod
    def for_inference(model): ...
    @staticmethod
    def for_training(model, use_gradient_checkpointing: bool = True): ...
