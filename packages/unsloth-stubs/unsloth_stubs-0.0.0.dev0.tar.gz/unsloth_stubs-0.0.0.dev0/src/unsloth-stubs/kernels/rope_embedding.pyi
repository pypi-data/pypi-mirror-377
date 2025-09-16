import torch
from .utils import calculate_settings as calculate_settings, torch_device_stream as torch_device_stream, torch_gpu_device as torch_gpu_device

ROPE_GROUP_SIZE: int

class Fast_RoPE_Embedding(torch.autograd.Function):
    @staticmethod
    def forward(ctx, Q, cos, sin): ...
    @staticmethod
    def backward(ctx, dY): ...

@torch.compiler.disable
def fast_rope_embedding(Q, K, cos, sin): ...

class Slow_RoPE_Embedding(torch.autograd.Function):
    @staticmethod
    def forward(ctx, Q, cos, sin, position_ids): ...
    @staticmethod
    def backward(ctx, dY): ...

def inplace_rope_embedding(Q, K, cos, sin, position_ids): ...
