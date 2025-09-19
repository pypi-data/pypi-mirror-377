from typing import List, Dict, Optional
from databricks_cli.workspace.api import WorkspaceFileInfo, WorkspaceApi
from pyspark.sql import DataFrame, functions as F

from odap.common.logger import logger
from odap.common.config import TIMESTAMP_COLUMN
from odap.common.databricks import get_workspace_api
from odap.common.dataframes import create_dataframe_from_notebook_cells
from odap.common.notebook import eval_cell_with_header, get_notebook_cells

from odap.feature_factory import const
from odap.feature_factory.config import (
    Config,
    get_feature_source_prefix,
)
from odap.feature_factory.dataframes.dataframe_checker import check_feature_df
from odap.feature_factory.feature_notebooks_selection import get_list_of_selected_feature_notebooks
from odap.feature_factory.metadata import resolve_metadata, set_fs_compatible_metadata, set_metadata_backfill_info
from odap.feature_factory.metadata_schema import FeaturesMetadataType
from odap.feature_factory.no_target_optimizer import replace_no_target


class FeatureNotebook:
    def __init__(
        self,
        notebook_info: WorkspaceFileInfo,
        df: DataFrame,
        metadata: FeaturesMetadataType,
        config: Config,
        df_checks: List[str],
    ):
        self.info = notebook_info
        self.df = df
        self.metadata = metadata
        self.df_checks = df_checks

        self.post_load_actions(config)

    @classmethod
    def from_api(
        cls, notebook_info: WorkspaceFileInfo, config: Config, workspace_api: WorkspaceApi, prefix: Optional[str]
    ):
        info = notebook_info
        cells = get_feature_notebook_cells(notebook_info, workspace_api, config)
        entity_primary_key = config.get_entity_primary_key()
        df = create_dataframe_from_notebook_cells(info, cells[:])
        df_prefixed = prefix_columns(df, entity_primary_key, prefix)

        metadata = resolve_metadata(cells, info.path, df_prefixed, config.get_entity_primary_key(), prefix)
        df_check_list = get_dq_checks_list(info, cells)

        return cls(info, df_prefixed, metadata, config, df_check_list)

    def post_load_actions(self, config: Config):
        entity_primary_key = config.get_entity_primary_key()

        set_fs_compatible_metadata(self.metadata, config)

        set_metadata_backfill_info(self.metadata, config)

        check_feature_df(self.df, entity_primary_key, self.metadata, self.info.path)

        logger.info(f"Feature {self.info.path} successfully loaded.")


FeatureNotebookList = List[FeatureNotebook]


def prefix_columns(df: DataFrame, entity_primary_key: str, prefix: Optional[str]) -> DataFrame:
    if not prefix:
        return df

    primary_key = [entity_primary_key, TIMESTAMP_COLUMN]
    renamed_columns = [F.col(col).alias(f"{prefix}_{col}") if col not in primary_key else col for col in df.columns]
    return df.select(*renamed_columns)


def get_feature_notebook_cells(info: WorkspaceFileInfo, workspace_api: WorkspaceApi, config: Config) -> List[str]:
    notebook_cells = get_notebook_cells(info, workspace_api)
    if config.use_no_target_optimization():
        replace_no_target(info.language, notebook_cells)
    return notebook_cells


def load_feature_notebooks(
    config: Config, notebooks_info: List[WorkspaceFileInfo], prefix: Optional[str]
) -> FeatureNotebookList:
    workspace_api = get_workspace_api()

    feature_notebooks = []

    for info in notebooks_info:
        feature_notebooks.append(FeatureNotebook.from_api(info, config, workspace_api, prefix))

    return feature_notebooks


def create_notebook_table_mapping(feature_notebooks: FeatureNotebookList) -> Dict[str, FeatureNotebookList]:
    mapping = {}

    for feature_notebook in feature_notebooks:
        table = feature_notebook.metadata[0].get("table", None)

        if table not in mapping:
            mapping[table] = []

        mapping[table].append(feature_notebook)
    return mapping


def get_dq_checks_list(info, cells) -> List[str]:
    checks_list = eval_cell_with_header(cells, info.path, const.DQ_CHECKS_HEADER_REGEX, const.DQ_CHECKS)

    return checks_list or []


def get_feature_notebooks_from_dirs(config: Config) -> FeatureNotebookList:
    feature_sources = config.get_feature_sources()
    feature_notebooks = []

    for feature_source in feature_sources:
        prefix = get_feature_source_prefix(feature_source)

        notebooks_info = get_list_of_selected_feature_notebooks(feature_source)
        notebooks_loaded = load_feature_notebooks(config, notebooks_info, prefix)

        feature_notebooks.extend(notebooks_loaded)

    return feature_notebooks
