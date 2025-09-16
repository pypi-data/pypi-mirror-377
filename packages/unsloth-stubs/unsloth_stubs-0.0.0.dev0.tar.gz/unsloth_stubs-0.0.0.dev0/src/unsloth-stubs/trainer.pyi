from _typeshed import Incomplete
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth_zoo.vision_utils import UnslothVisionDataCollator as UnslothVisionDataCollator

__all__ = ['UnslothTrainingArguments', 'UnslothTrainer', 'unsloth_train', '_patch_trl_trainer', 'UnslothVisionDataCollator']

def unsloth_train(trainer, *args, **kwargs): ...

class UnslothTrainingArguments(TrainingArguments):
    def __init__(self, embedding_learning_rate: float = None, *args, **kwargs) -> None: ...

class UnslothTrainer(SFTTrainer):
    optimizer: Incomplete
    def create_optimizer(self): ...

def _patch_trl_trainer() -> None: ...
