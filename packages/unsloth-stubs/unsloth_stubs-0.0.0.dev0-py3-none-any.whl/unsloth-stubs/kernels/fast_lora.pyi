import torch
from .geglu import geglu_approx_backward_kernel as geglu_approx_backward_kernel, geglu_approx_forward_kernel as geglu_approx_forward_kernel, geglu_exact_backward_kernel as geglu_exact_backward_kernel, geglu_exact_forward_kernel as geglu_exact_forward_kernel
from .swiglu import swiglu_DWf_DW_dfg_kernel as swiglu_DWf_DW_dfg_kernel, swiglu_fg_kernel as swiglu_fg_kernel
from .utils import QUANT_STATE as QUANT_STATE, fast_dequantize as fast_dequantize, get_lora_parameters as get_lora_parameters, get_lora_parameters_bias as get_lora_parameters_bias, matmul_lora as matmul_lora, torch_amp_custom_bwd as torch_amp_custom_bwd, torch_amp_custom_fwd as torch_amp_custom_fwd
from _typeshed import Incomplete

class LoRA_MLP(torch.autograd.Function):
    @staticmethod
    @torch_amp_custom_fwd
    def forward(ctx, X: torch.Tensor, gateW, gateW_quant, gateA, gateB, gateS, upW, upW_quant, upA, upB, upS, downW, downW_quant, downA, downB, downS, _forward_function, _backward_function, inplace: bool = True): ...
    @staticmethod
    @torch_amp_custom_bwd
    def backward(ctx, dY: torch.Tensor): ...

def apply_lora_mlp_swiglu(self, X, inplace: bool = True): ...
def apply_lora_mlp_geglu_exact(self, X, inplace: bool = True): ...
def apply_lora_mlp_geglu_approx(self, X): ...

class LoRA_QKV(torch.autograd.Function):
    @staticmethod
    @torch_amp_custom_fwd
    def forward(ctx, X: torch.Tensor, QW, QW_quant, QA, QB, QS, KW, KW_quant, KA, KB, KS, VW, VW_quant, VA, VB, VS, inplace: bool = True): ...
    @staticmethod
    @torch_amp_custom_bwd
    def backward(ctx, dQ, dK, dV): ...

def apply_lora_qkv(self, X, inplace: bool = True): ...

class LoRA_W(torch.autograd.Function):
    @staticmethod
    @torch_amp_custom_fwd
    def forward(ctx, X: torch.Tensor, W, W_quant, A, B, S): ...
    @staticmethod
    @torch_amp_custom_bwd
    def backward(ctx, dY: torch.Tensor): ...

def apply_lora_o(self, X): ...

IDENTITY_DROPOUT: Incomplete

@torch._disable_dynamo
def fast_lora_forward(self, x: torch.Tensor, *args, **kwargs) -> torch.Tensor: ...
