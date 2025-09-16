import functools
from _typeshed import Incomplete
from functools import lru_cache as lru_cache
from transformers.models.llama.modeling_llama import logger as logger

torch_compile_options: Incomplete
HAS_FLEX_ATTENTION: bool

def slow_attention_softcapping(Q, K, V, causal_mask, self, bsz, q_len): ...

create_flex_attention_causal_mask: Incomplete
create_flex_attention_sliding_window_mask: Incomplete

def generate_tanh_softcap(t): ...
def causal_masker(b, h, q_idx, kv_idx): ...
@functools.lru_cache
def sliding_window_masker(size: int = 4096): ...
@functools.lru_cache
def create_block_mask(mask, n: int = 128): ...
@functools.lru_cache
def flex_attention(s, t): ...

torch_matmul: Incomplete
torch_tanh: Incomplete
torch_nn_functional_softmax: Incomplete

def slow_inference_attention_softcapping(Q, K, V, causal_mask, self, bsz, q_len): ...
