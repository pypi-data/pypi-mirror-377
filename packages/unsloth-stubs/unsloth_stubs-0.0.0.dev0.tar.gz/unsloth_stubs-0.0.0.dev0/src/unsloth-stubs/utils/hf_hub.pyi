from _typeshed import Incomplete
from huggingface_hub import ModelInfo as ModelInfo

POPULARITY_PROPERTIES: Incomplete
THOUSAND: int
MILLION: int
BILLION: int

def formatted_int(value: int) -> str: ...
def get_model_info(model_id: str, properties: list[str] = ['safetensors', 'lastModified']) -> ModelInfo: ...
def list_models(properties: list[str] = None, full: bool = False, sort: str = 'downloads', author: str = 'unsloth', search: str = None, limit: int = 10) -> list[ModelInfo]: ...
