import ctypes
import torch
import triton
from _typeshed import Incomplete
from unsloth import DEVICE_COUNT as DEVICE_COUNT, DEVICE_TYPE as DEVICE_TYPE

MAX_FUSED_SIZE: int
next_power_of_2: Incomplete
torch_Tensor: Incomplete
torch_amp_custom_fwd: Incomplete
torch_amp_custom_bwd: Incomplete
triton_tanh: Incomplete
triton_cast: Incomplete

def calculate_settings(n: int) -> tuple[int, int]: ...

HAS_CUDA_STREAM: bool
HAS_XPU_STREAM: bool

def get_ptr(x: torch.Tensor | None): ...

get_ptr: Incomplete
torch_gpu_device: Incomplete
c_void_p = ctypes.c_void_p
XPU_STREAMS: Incomplete
WEIGHT_BUFFERS: Incomplete
ABSMAX_BUFFERS: Incomplete
CUDA_STREAMS: Incomplete
ctypes_c_int = ctypes.c_int
ctypes_c_int32 = ctypes.c_int32

def cdequantize_blockwise_fp32(*args, **kwargs) -> None: ...
def cdequantize_blockwise_fp16_nf4(*args, **kwargs) -> None: ...
def cdequantize_blockwise_bf16_nf4(*args, **kwargs) -> None: ...
def cgemm_4bit_inference_naive_fp16(*args, **kwargs) -> None: ...
def cgemm_4bit_inference_naive_bf16(*args, **kwargs) -> None: ...

cdequantize_blockwise_fp32: Incomplete
cdequantize_blockwise_fp16_nf4: Incomplete
cdequantize_blockwise_bf16_nf4: Incomplete
cgemm_4bit_inference_naive_fp16: Incomplete
cgemm_4bit_inference_naive_bf16: Incomplete
torch_device_stream: Incomplete
torch_mm: Incomplete
torch_mv: Incomplete
torch_matmul: Incomplete
torch_addmm: Incomplete
torch_empty: Incomplete
torch_float32: Incomplete
torch_float16: Incomplete
torch_bfloat16: Incomplete

def QUANT_STATE(W): ...
def get_lora_parameters(proj): ...
def get_lora_parameters_bias(proj): ...
@torch.inference_mode
def fast_dequantize(W, quant_state=None, out=None, use_global_buffer: bool = False): ...
def fast_gemv(X, W, quant_state, out=None): ...
def fast_linear_forward(proj, X, temp_lora=None, out=None): ...
def matmul_lora(X, W, W_quant, A, B, s, out=None): ...
