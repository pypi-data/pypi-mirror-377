from .llama import *
from ._utils import __version__ as __version__
from .llama import LlamaLinearScalingRotaryEmbedding as LlamaLinearScalingRotaryEmbedding, LlamaRotaryEmbedding as LlamaRotaryEmbedding
from _typeshed import Incomplete
from transformers.models.qwen3.modeling_qwen3 import Qwen3Attention

transformers_version: Incomplete
Qwen3SdpaAttention = Qwen3Attention
Qwen3FlashAttention2 = Qwen3Attention

def Qwen3Attention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]: ...

torch_matmul: Incomplete

def Qwen3Attention_fast_forward_inference(self, hidden_states: torch.Tensor, past_key_value: Optional[Tuple[torch.Tensor]], position_ids, do_prefill: bool = False, attention_mask=None): ...

class FastQwen3Model(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def from_pretrained(model_name: str = 'Qwen/Qwen3-7B', max_seq_length: int = 4096, dtype=None, load_in_4bit: bool = True, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, model_patcher=None, tokenizer_name=None, trust_remote_code: bool = False, **kwargs): ...
