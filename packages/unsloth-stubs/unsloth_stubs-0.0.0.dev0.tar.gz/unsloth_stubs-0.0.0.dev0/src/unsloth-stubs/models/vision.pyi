from ._utils import *
from transformers import AutoModelForImageTextToText

__all__ = ['FastBaseModel']

AutoModelForVision2Seq = AutoModelForImageTextToText

class FastBaseModel:
    @staticmethod
    def from_pretrained(model_name: str = 'unsloth/Llama-3.2-1B-Instruct', max_seq_length: int = 2048, dtype=None, load_in_4bit: bool = True, load_in_8bit: bool = False, full_finetuning: bool = False, token=None, device_map: str = 'sequential', trust_remote_code: bool = False, model_types=None, tokenizer_name=None, auto_model=..., use_gradient_checkpointing: str = 'unsloth', supports_sdpa: bool = True, whisper_language=None, whisper_task=None, **kwargs): ...
    @staticmethod
    def get_peft_model(model, r: int = 16, target_modules=None, lora_alpha: int = 16, lora_dropout: float = 0.0, bias: str = 'none', finetune_vision_layers: bool = True, finetune_language_layers: bool = True, finetune_attention_modules: bool = True, finetune_mlp_modules: bool = True, layers_to_transform=None, layers_pattern=None, use_gradient_checkpointing: str = 'unsloth', random_state: int = 3407, max_seq_length: int = 2048, use_rslora: bool = False, modules_to_save=None, init_lora_weights: bool = True, loftq_config={}, task_type=..., temporary_location: str = '_unsloth_temporary_saved_buffers', **kwargs): ...
    @staticmethod
    def post_patch_model(model, use_gradient_checkpointing: bool = True, trust_remote_code: bool = False): ...
    @staticmethod
    def for_inference(model): ...
    @staticmethod
    def for_training(model, use_gradient_checkpointing: bool = True): ...
