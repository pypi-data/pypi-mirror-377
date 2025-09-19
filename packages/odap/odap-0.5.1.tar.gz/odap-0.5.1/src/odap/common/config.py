from typing import Dict, Any
import os
import enum
import yaml
from odap.common.utils import get_project_root_fs_path
from odap.common.exceptions import ConfigAttributeMissingException, WriteEnvNotSetException


CONFIG_NAME_DEFAULT = "config.yaml"
TIMESTAMP_COLUMN = "timestamp"
ENV_PLACEHOLDER = "{write_env}"
CATALOG_PLACEHOLDER = "{catalog}"

Config = Dict[str, Any]


class ConfigNamespace(enum.Enum):
    FEATURE_FACTORY = "featurefactory"
    SEGMENT_FACTORY = "segmentfactory"
    USECASE_FACTORY = "usecasefactory"


def load_yaml(config_path):
    with open(config_path, "r", encoding="utf-8") as stream:
        raw_config = resolve_env(stream.read())
        config = yaml.safe_load(raw_config)

    return config


def update_configs(common: dict, entity: dict) -> dict:
    for key, value in entity.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recursively update the nested dictionary
            common[key] = update_configs(common.get(key, {}), value)
        elif isinstance(value, list):
            # If the value is a list, directly overwrite the list in common
            common[key] = value
        else:
            # For other types, directly replace the value in common
            common[key] = value
    return common


def check_for_feature_source(input_dict: dict):
    def check_list(lst):
        for item in lst:
            if isinstance(item, dict):
                check_dict(item)

    def check_dict(config_common):
        for key, value in config_common.items():
            if key == "feature_sources":
                raise ValueError(
                    "The 'feature_sources' must be defined only in entity config, please remove them from common config"
                )
            if isinstance(value, dict):
                check_dict(value)
            elif isinstance(value, list):
                check_list(value)

    check_dict(input_dict)


def update_configs_pipeline(base_path, config):
    config_common_path = os.path.join(base_path, os.environ.get("ODAP_CONFIG_PATH_COMMON"))

    config_common = load_yaml(config_common_path)

    check_for_feature_source(config_common)

    updated_config = update_configs(config_common, config)

    return updated_config


def resolve_env(raw_config: str):
    env = os.environ.get("WRITE_ENV")

    if ENV_PLACEHOLDER in raw_config and not env:
        raise WriteEnvNotSetException(
            f"Config.yaml contains placeholder {ENV_PLACEHOLDER} but env variable WRITE_ENV is not set."
        )

    if env:
        raw_config = raw_config.replace(ENV_PLACEHOLDER, env)

    catalog = os.environ.get("CATALOG")

    if catalog:
        raw_config = raw_config.replace(CATALOG_PLACEHOLDER, catalog)

    return raw_config


def get_config_on_rel_path(*rel_path: str) -> Config:
    base_path = get_project_root_fs_path()
    config_path = os.path.join(base_path, *rel_path)

    config = load_yaml(config_path)

    if os.environ.get("ODAP_CONFIG_PATH_COMMON"):
        config = update_configs_pipeline(base_path, config)

    parameters = config.get("parameters", None)

    if not parameters:
        raise ConfigAttributeMissingException(f"'parameters' not defined in {os.path.join(*rel_path)}")
    return parameters


def get_config_namespace(namespace: ConfigNamespace) -> Config:
    config_path = get_config_file_name()
    parameters = get_config_on_rel_path(config_path)

    config = parameters.get(namespace.value, None)

    if not config:
        raise ConfigAttributeMissingException(f"'{namespace.value}' not defined in {config_path}")

    return config


def get_config_file_name() -> str:
    file_path = os.environ.get("ODAP_CONFIG_PATH_ENTITY")

    return file_path if file_path else CONFIG_NAME_DEFAULT
