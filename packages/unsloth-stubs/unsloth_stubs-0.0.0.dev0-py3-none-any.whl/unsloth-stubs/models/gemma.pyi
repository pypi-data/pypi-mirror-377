from .llama import *
from ._utils import __version__ as __version__
from _typeshed import Incomplete
from transformers.models.gemma.modeling_gemma import GemmaAttention, GemmaRotaryEmbedding as GemmaRotaryEmbedding, apply_rotary_pos_emb as apply_rotary_pos_emb, repeat_kv as repeat_kv

transformers_version: Incomplete
GemmaSdpaAttention = GemmaAttention
GemmaFlashAttention2 = GemmaAttention
torch_nn_functional_gelu: Incomplete

def fast_geglu_inference(self, X): ...
def GemmaDecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, padding_mask: Optional[torch.LongTensor] = None, *args, **kwargs): ...
def GemmaModel_fast_forward_inference(self, input_ids, past_key_values, position_ids, attention_mask=None): ...

class GemmaFixedRotaryEmbedding(torch.nn.Module):
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

class GemmaFixedLinearScalingRotaryEmbedding(GemmaFixedRotaryEmbedding):
    scaling_factor: Incomplete
    def __init__(self, dim=None, max_position_embeddings: int = 2048, base: int = 10000, device=None, scaling_factor: float = 1.0, config=None) -> None: ...

class FastGemmaModel(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def post_patch(model, tokenizer): ...
