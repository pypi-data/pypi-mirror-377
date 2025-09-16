from .llama import *
from ._utils import __version__ as __version__
from _typeshed import Incomplete
from transformers.models.cohere.modeling_cohere import CohereAttention, CohereRotaryEmbedding as CohereRotaryEmbedding, apply_rotary_pos_emb as apply_rotary_pos_emb, repeat_kv as repeat_kv

transformers_version: Incomplete
CohereSdpaAttention = CohereAttention
CohereFlashAttention2 = CohereAttention

def fast_layernorm_inference(self, X, out_weight=None): ...
def CohereAttention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]: ...
def CohereDecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs): ...

KV_CACHE_INCREMENT: int
torch_nn_functional_softmax: Incomplete
torch_matmul: Incomplete

def CohereAttention_fast_forward_inference(self, hidden_states: torch.Tensor, past_key_value: Optional[Tuple[torch.Tensor]], position_ids, do_prefill: bool = False, attention_mask=None): ...
def CohereModel_fast_forward_inference(self, input_ids, past_key_values, position_ids, attention_mask=None): ...

class FastCohereModel(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
