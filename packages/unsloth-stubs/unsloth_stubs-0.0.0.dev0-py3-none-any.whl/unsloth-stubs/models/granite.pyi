from .llama import *
from .mistral import *
from ._utils import __version__ as __version__
from .llama import LlamaLinearScalingRotaryEmbedding as LlamaLinearScalingRotaryEmbedding, LlamaRotaryEmbedding as LlamaRotaryEmbedding
from _typeshed import Incomplete
from transformers.models.granite.modeling_granite import GraniteAttention

transformers_version: Incomplete
GraniteSdpaAttention = GraniteAttention
GraniteFlashAttention2 = GraniteAttention

def GraniteAttention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]: ...
def GraniteDecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs): ...

KV_CACHE_INCREMENT: int
torch_nn_functional_softmax: Incomplete
torch_matmul: Incomplete
torch_tanh: Incomplete

def GraniteAttention_fast_forward_inference(self, hidden_states: torch.Tensor, past_key_value: Optional[Tuple[torch.Tensor]], position_ids, do_prefill: bool = False, attention_mask=None, use_sliding_window: bool = False, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None): ...
def GraniteModel_fast_forward_inference(self, input_ids, past_key_values, position_ids, attention_mask=None): ...

class GraniteRotaryEmbedding(LlamaRotaryEmbedding):
    def __init__(self, config) -> None: ...

def patched_init(original_init): ...

class FastGraniteModel(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def post_patch(model, tokenizer): ...
