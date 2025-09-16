from .llama import *
from ._utils import __version__ as __version__
from .llama import LlamaLinearScalingRotaryEmbedding as LlamaLinearScalingRotaryEmbedding, LlamaRotaryEmbedding as LlamaRotaryEmbedding
from .qwen3 import FastQwen3Model as FastQwen3Model, Qwen3Attention_fast_forward as Qwen3Attention_fast_forward
from _typeshed import Incomplete
from unsloth_zoo.utils import Version as Version

torch_nn_functional_softmax: Incomplete

def Qwen3MoeSparseMoeBlock_fast_forward(self, X, temp_gate=None, temp_up=None): ...
def Qwen3MoeDecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, output_router_logits: Optional[bool] = False, use_cache: Optional[bool] = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs): ...

class FastQwen3MoeModel(FastQwen3Model):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def from_pretrained(model_name: str = 'Qwen/Qwen3-7B', max_seq_length: int = 4096, dtype=None, load_in_4bit: bool = True, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, model_patcher=None, tokenizer_name=None, trust_remote_code: bool = False, **kwargs): ...
