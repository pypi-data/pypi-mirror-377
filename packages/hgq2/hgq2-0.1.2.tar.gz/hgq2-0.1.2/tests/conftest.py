import os
import random
from pathlib import Path

import keras
import numpy as np
import pytest


@pytest.fixture(scope='session', autouse=True, params=[42])
def set_random_seed(request):
    """Set random seeds for reproducibility"""

    seed = request.param
    np.random.seed(seed)
    random.seed(seed)
    backend = keras.backend.backend()
    match backend:
        case 'tensorflow':
            import tensorflow as tf

            tf.random.set_seed(seed)
            for device in tf.config.list_physical_devices('GPU'):
                tf.config.experimental.set_memory_growth(device, True)
        case 'torch':
            import torch

            torch.manual_seed(seed)
        case 'jax':
            pass
        case _:
            raise ValueError(f'Unknown backend: {backend}')


@pytest.fixture(scope='session', autouse=True)
def configure_backend():
    backend = keras.backend.backend()

    match backend:
        case 'tensorflow':
            import tensorflow as tf

            tf.config.threading.set_intra_op_parallelism_threads(1)
        case 'torch':
            import torch

            torch.set_float32_matmul_precision('highest')
        case 'jax':
            pass
        case _:
            raise ValueError(f'Unknown backend: {backend}')


@pytest.fixture(scope='session', autouse=True)
def set_hls4ml_configs():
    """Set default hls4ml configuration"""
    os.environ['HLS4ML_BACKEND'] = 'Vivado'


@pytest.fixture(scope='function')
def temp_directory(request: pytest.FixtureRequest):
    root = Path(os.environ.get('HGQ2_TEST_DIR', '/tmp/hgq2_test'))
    root.mkdir(exist_ok=True)

    test_name = request.node.name
    cls_name = request.cls.__name__ if request.cls else None
    if cls_name is None:
        test_dir = root / test_name
    else:
        test_dir = root / f'{cls_name}.{test_name}'
    test_dir.mkdir(exist_ok=True)
    return str(test_dir)


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    root = Path(os.environ.get('HGQ2_TEST_DIR', '/tmp/hgq2_test'))
    # Purge empty directories
    for path in root.glob('*'):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
