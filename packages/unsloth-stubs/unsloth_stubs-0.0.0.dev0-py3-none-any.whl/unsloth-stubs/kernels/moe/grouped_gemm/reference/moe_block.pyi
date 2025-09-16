import torch
from _typeshed import Incomplete
from grouped_gemm.kernels.tuning import KernelConfigBackward_dW as KernelConfigBackward_dW, KernelConfigBackward_dX as KernelConfigBackward_dX, KernelConfigForward as KernelConfigForward
from grouped_gemm.reference.moe_ops import Qwen3MoeGroupedGEMMBlock
from transformers.models.qwen3_moe.configuration_qwen3_moe import Qwen3MoeConfig as Qwen3MoeConfig
from transformers.models.qwen3_moe.modeling_qwen3_moe import Qwen3MoeSparseMoeBlock as Qwen3MoeSparseMoeBlock

class Qwen3MoeFusedGroupedGEMMBlock(Qwen3MoeGroupedGEMMBlock):
    permute_x: Incomplete
    permute_y: Incomplete
    autotune: Incomplete
    kernel_config_fwd: Incomplete
    kernel_config_bwd_dW: Incomplete
    kernel_config_bwd_dX: Incomplete
    dW_only: Incomplete
    dX_only: Incomplete
    def __init__(self, config: Qwen3MoeConfig, gate: torch.Tensor, gate_up_proj: torch.Tensor, down_proj: torch.Tensor, permute_x: bool = True, permute_y: bool = True, autotune: bool = True, kernel_config_fwd: KernelConfigForward = None, kernel_config_bwd_dW: KernelConfigBackward_dW = None, kernel_config_bwd_dX: KernelConfigBackward_dX = None, dW_only: bool = False, dX_only: bool = False) -> None: ...
    @classmethod
    def from_hf(cls, moe_block: Qwen3MoeSparseMoeBlock, permute_x: bool = True, permute_y: bool = True, autotune: bool = True, kernel_config_fwd: KernelConfigForward = None, kernel_config_bwd_dW: KernelConfigBackward_dW = None, kernel_config_bwd_dX: KernelConfigBackward_dX = None, dW_only: bool = False, dX_only: bool = False): ...
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: ...
