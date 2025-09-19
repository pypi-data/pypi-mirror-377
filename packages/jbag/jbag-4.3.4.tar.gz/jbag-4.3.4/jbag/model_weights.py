import os.path
from typing import Optional

import torch
from torch import nn
from torch.nn import DataParallel
from torch.nn.parallel import DistributedDataParallel
from torch.optim import Optimizer

from jbag.io import ensure_output_file_dir_existence
from jbag.log import logger

MODEL_STATE = "Model_state"
OPTIMIZER_STATE = "Optimizer_state"


def get_unwrapped_model(model: nn.Module):
    if isinstance(model, (DataParallel, DistributedDataParallel)):
        model = model.module
    return model


def save_checkpoint(file: str, model: nn.Module, optimizer: Optional[Optimizer] = None,
                    **kwargs):
    checkpoint = {MODEL_STATE: get_unwrapped_model(model).state_dict()}
    if optimizer:
        checkpoint[OPTIMIZER_STATE] = optimizer.state_dict()

    overlap = {MODEL_STATE, OPTIMIZER_STATE} & kwargs.keys()
    if overlap:
        raise KeyError(f"Kwargs contain reserved keys: {overlap}.")
    checkpoint.update(kwargs)
    ensure_output_file_dir_existence(file)
    torch.save(checkpoint, file)
    logger.info(f"Checkpoint saved to {file}.")


def load_checkpoint(checkpoint_file: str, model: Optional[nn.Module] = None,
                    optimizer: Optional[Optimizer] = None, map_location=None):
    if not os.path.isfile(checkpoint_file):
        raise FileNotFoundError(f"Input checkpoint file {checkpoint_file} not found.")
    checkpoint = torch.load(checkpoint_file, map_location=map_location)
    if model is not None:
        model_state = checkpoint.get(MODEL_STATE)
        if model_state is not None:
            get_unwrapped_model(model).load_state_dict(model_state)
            logger.info(f"Model state loaded from {checkpoint_file}.")
        else:
            logger.warning(f"{checkpoint_file} does not include model state.")

    if optimizer is not None:
        optimizer_state = checkpoint.get(OPTIMIZER_STATE)
        if optimizer_state is not None:
            optimizer.load_state_dict(optimizer_state)
            logger.info(f"Optimizer state loaded from {checkpoint_file}.")
        else:
            logger.warning(f"{checkpoint_file} does not include optimizer state.")

    return checkpoint
