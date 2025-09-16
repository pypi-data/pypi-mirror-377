import os
from typing import List

import hydra
import yaml
from omegaconf import DictConfig
from yacs.config import CfgNode


def init_yacs_config(config_path: str, config_overrides: List[str] = None) -> CfgNode:
    with open(config_path, 'r') as f:
        cfg_data = yaml.safe_load(f)
        cfg = CfgNode(cfg_data)

    # Apply overrides
    if config_overrides:
        cfg.merge_from_list(config_overrides)
    return cfg


def init_hydra_config(cfg_path: str, overrides: List[str]) -> DictConfig:
    config_dir, config_name = os.path.split(os.path.abspath(cfg_path))
    # Hydra since version 1.2 supports backwards compatible upgrades by default through the use of
    # the version_base parameter to @hydra.main() and hydra.initialize().
    compatibility_key = dict(version_base='v1.1') if hydra.__version__ >= '1.2' else dict()
    with hydra.initialize_config_dir(config_dir=config_dir, **compatibility_key):
        cfg = hydra.compose(config_name=config_name, overrides=overrides)
    return cfg
