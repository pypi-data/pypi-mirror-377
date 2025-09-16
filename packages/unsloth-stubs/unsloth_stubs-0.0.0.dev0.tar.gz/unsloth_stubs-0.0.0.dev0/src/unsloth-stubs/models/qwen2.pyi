from .llama import *
from .llama import LlamaLinearScalingRotaryEmbedding as LlamaLinearScalingRotaryEmbedding, LlamaRotaryEmbedding as LlamaRotaryEmbedding
from transformers.models.qwen2.modeling_qwen2 import Qwen2Attention

Qwen2SdpaAttention = Qwen2Attention
Qwen2FlashAttention2 = Qwen2Attention

class FastQwen2Model(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def from_pretrained(model_name: str = 'Qwen/Qwen2-7B', max_seq_length: int = 4096, dtype=None, load_in_4bit: bool = True, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, model_patcher=None, tokenizer_name=None, trust_remote_code: bool = False, **kwargs): ...
