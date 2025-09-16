from .llama import *
from ._utils import __version__ as __version__
from .gemma import GemmaFixedLinearScalingRotaryEmbedding as GemmaFixedLinearScalingRotaryEmbedding, GemmaFixedRotaryEmbedding as GemmaFixedRotaryEmbedding, fast_geglu_inference as fast_geglu_inference
from _typeshed import Incomplete
from transformers.models.gemma2.modeling_gemma2 import Gemma2Attention, Gemma2RotaryEmbedding as Gemma2RotaryEmbedding, apply_rotary_pos_emb as apply_rotary_pos_emb, repeat_kv as repeat_kv

transformers_version: Incomplete
Gemma2SdpaAttention = Gemma2Attention
Gemma2FlashAttention2 = Gemma2Attention

def Gemma2Attention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: Optional[torch.LongTensor] = None, *args, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]: ...
def Gemma2DecoderLayer_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, padding_mask: Optional[torch.LongTensor] = None, *args, **kwargs): ...

KV_CACHE_INCREMENT: int
torch_nn_functional_softmax: Incomplete
torch_matmul: Incomplete
torch_tanh: Incomplete

def Gemma2Attention_fast_forward_inference(self, hidden_states: torch.Tensor, past_key_value: Optional[Tuple[torch.Tensor]], position_ids, do_prefill: bool = False, attention_mask=None, use_sliding_window: bool = False): ...
def Gemma2Model_fast_forward_inference(self, input_ids, past_key_values, position_ids, attention_mask=None): ...

class FastGemma2Model(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def post_patch(model, tokenizer): ...
