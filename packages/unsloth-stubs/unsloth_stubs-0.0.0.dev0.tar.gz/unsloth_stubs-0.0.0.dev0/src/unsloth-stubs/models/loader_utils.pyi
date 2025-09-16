from .mapper import FLOAT_TO_INT_MAPPER as FLOAT_TO_INT_MAPPER, INT_TO_FLOAT_MAPPER as INT_TO_FLOAT_MAPPER, MAP_TO_UNSLOTH_16bit as MAP_TO_UNSLOTH_16bit
from _typeshed import Incomplete

SUPPORTS_FOURBIT: Incomplete
BAD_MAPPINGS: Incomplete

def get_model_name(model_name, load_in_4bit: bool = True): ...
