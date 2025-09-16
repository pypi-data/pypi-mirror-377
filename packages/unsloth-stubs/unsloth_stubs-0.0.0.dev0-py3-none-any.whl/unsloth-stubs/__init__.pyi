from .models import *
from .save import *
from .chat_templates import *
from .tokenizer_utils import *
from .trainer import *
import functools
from .models import __version__ as __version__
from _typeshed import Incomplete
from pathlib import Path as Path

critical_modules: Incomplete
already_imported: Incomplete

@functools.cache
def is_hip(): ...
@functools.cache
def get_device_type(): ...

DEVICE_TYPE: str

@functools.cache
def get_device_count(): ...

DEVICE_COUNT: int
torch_version: Incomplete
major_torch: Incomplete
minor_torch: Incomplete
major_version: Incomplete
minor_version: Incomplete
SUPPORTS_BFLOAT16: Incomplete
old_is_bf16_supported: Incomplete

def is_bf16_supported(including_emulation: bool = False): ...

libcuda_dirs: Incomplete
cdequantize_blockwise_fp32: Incomplete
possible_cudas: Incomplete
find_cuda: Incomplete
find_number: Incomplete
latest_cuda: Incomplete
latest_cuda = possible_cudas[latest_cuda]
unsloth_zoo_version: Incomplete
