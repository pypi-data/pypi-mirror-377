from .llama import *
from ._utils import __version__ as __version__
from .llama import LlamaLinearScalingRotaryEmbedding as LlamaLinearScalingRotaryEmbedding, LlamaRotaryEmbedding as LlamaRotaryEmbedding
from transformers.models.mistral.modeling_mistral import MistralAttention
from unsloth_zoo.utils import Version as Version

MistralSdpaAttention = MistralAttention
MistralFlashAttention2 = MistralAttention

def MistralAttention_fast_forward(self, hidden_states: torch.Tensor, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False, padding_mask: Optional[torch.LongTensor] = None, position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, *args, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]: ...
def MistralForCausalLM_fast_forward(self, input_ids: torch.LongTensor = None, causal_mask: Optional[BlockDiagonalCausalMask] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None, inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, num_logits_to_keep: Optional[int] = 0, logits_to_keep: Optional[int] = 0, *args, **kwargs) -> Union[Tuple, CausalLMOutputWithPast]: ...
def patch_mistral_nemo_attention(function): ...

class FastMistralModel(FastLlamaModel):
    @staticmethod
    def pre_patch() -> None: ...
    @staticmethod
    def from_pretrained(model_name: str = 'unsloth/mistral-7b-bnb-4bit', max_seq_length=None, dtype=None, load_in_4bit: bool = True, token=None, device_map: str = 'sequential', rope_scaling=None, fix_tokenizer: bool = True, model_patcher=None, tokenizer_name=None, trust_remote_code: bool = False, **kwargs): ...
