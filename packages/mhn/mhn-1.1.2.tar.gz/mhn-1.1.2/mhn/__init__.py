from . import optimizers
from . import model
from . import training
from . import full_state_space

from .utilities import set_seed

from .training.likelihood_cmhn import cuda_available
from .training.likelihood_cmhn import CUDA_AVAILABLE, CUDA_NOT_AVAILABLE, CUDA_NOT_FUNCTIONAL


def _get_metadata():
    import os
    meta_data = {'version': ">=1.1.0"}
    with open(os.path.join(os.path.dirname(__file__), "METADATA")) as f:
        for line in f.readlines():
            key, value = line.split()
            meta_data[key] = value
    return meta_data


_meta_data = _get_metadata()
__version__ = _meta_data["version"]

del _get_metadata, _meta_data
