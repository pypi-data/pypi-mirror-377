import torch
from .utils import MAX_FUSED_SIZE as MAX_FUSED_SIZE, calculate_settings as calculate_settings, torch_gpu_device as torch_gpu_device, triton_cast as triton_cast, triton_tanh as triton_tanh
from _typeshed import Incomplete
from transformers.models.llama.modeling_llama import logger as logger
from unsloth_zoo.loss_utils import post_patch_loss_function as post_patch_loss_function

class Fast_CrossEntropyLoss(torch.autograd.Function):
    @staticmethod
    def forward(ctx, logits, labels, logit_softcapping: float = 0, logit_scaling: float = 0): ...
    @staticmethod
    def backward(ctx, dlosses): ...

def fast_cross_entropy_loss(logits, labels, logit_softcapping: int = 0, logit_scaling: int = 0, n_items=None): ...

fast_cross_entropy_loss: Incomplete

def patch_loss_functions(torch_compile: bool = True) -> None: ...
