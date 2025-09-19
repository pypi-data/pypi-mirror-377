import os

from typing import Any

from pyspark.sql import SparkSession, functions as f
from delta import DeltaTable

from odap.common.databricks import resolve_dbutils

from odap.feature_factory.metadata_schema import (
    get_metadata_pk_columns,
)
from odap.common.logger import logger
from odap.common.config import TIMESTAMP_COLUMN
from odap.feature_factory.config import Config
from odap.common.databricks import spark
from odap.common.utils import get_project_root_fs_path
from odap.feature_factory.widgets import check_widget_existance


def run_notebook(notebook_path, params=None):
    dbutils = resolve_dbutils()

    if params is None:
        params = {}

    dbutils.notebook.run(notebook_path, 0, params)


# pylint: disable=too-many-statements
def get_orchestrator_path():
    default_file_relative_path = "orchestration/features_orchestrator"
    demo_file_relative_path = "odap_framework_demo/orchestration/features_orchestrator"

    repo_root_path = get_project_root_fs_path()

    default_full_file_path = os.path.join(repo_root_path, default_file_relative_path)
    demo_full_file_path = os.path.join(repo_root_path, demo_file_relative_path)

    if os.path.exists(default_full_file_path):
        return default_full_file_path

    if os.path.exists(demo_full_file_path):
        return demo_full_file_path

    demo_directory_path = os.path.join(repo_root_path, "odap_framework_demo")

    if os.path.exists(demo_directory_path):
        error_message = f"The file '{demo_file_relative_path}' does not exist. Please check its presence in the 'odap_framework_demo/orchestration' folder."
    else:
        error_message = f"The file '{default_file_relative_path}' does not exist. Please check the presence of features_orchestrator notebook in the orchestration folder, which must be placed at the repository root."

    raise FileNotFoundError(error_message)


# pylint: disable=unsubscriptable-object
def backfill(timestamps: list[str], **kwargs):
    for timestamp in timestamps:
        params = {"timestamp": timestamp, "target": "no target"}

        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_kwargs)

        notebook_path = get_orchestrator_path()

        run_notebook(notebook_path, params)


def get_missing_backfilled_metadata(config):
    metadata_path = config.get_metadata_table()

    df_metadata = spark.read.table(metadata_path)

    df_missing_backfill = (
        df_metadata.filter(f.col("backfilled") == "N").select("prefix", "notebook_name", "feature", "table").distinct()
    )

    return df_missing_backfill


def prepare_widget_value(value):
    joined_string_value = ",".join(value)

    return joined_string_value


def create_features_table_dict(config):
    df_missing_backfill = get_missing_backfilled_metadata(config)

    features_table_dict = {}

    df_missing_backfill_sources = [row["table"] for row in df_missing_backfill.select("table").distinct().collect()]

    for source in df_missing_backfill_sources:
        df_missing_backfill_one_source = df_missing_backfill.filter(f.col("table") == source)

        combined_notebooks_col = f.concat(f.lit("["), f.col("prefix"), f.lit("] "), f.col("notebook_name")).alias(
            "full_notebook_name"
        )

        new_feature_notebook_list = [
            row["full_notebook_name"]
            for row in df_missing_backfill_one_source.select(combined_notebooks_col).distinct().collect()
        ]

        new_feature_column_list = [row["feature"] for row in df_missing_backfill_one_source.select("feature").collect()]

        features_table_dict[source] = prepare_widget_value(new_feature_notebook_list), prepare_widget_value(
            new_feature_column_list
        )

    if len(features_table_dict) == 0:
        return None

    return features_table_dict


# def get_timestamps_to_backfill(config, table):

#     catalog = config.get_catalog()
#     entity = config.get_entity()
#     database = config.get_database_for_entity(entity)

#     timestamps_backfill_df = (
#         spark.read.table(f"{catalog}.{database}.{table}")
#         .select(f.col(TIMESTAMP_COLUMN).cast("string"))
#         .distinct()
#         .orderBy(f.desc(TIMESTAMP_COLUMN))
#     )

#     max_timestamp = timestamps_backfill_df.agg(f.max(TIMESTAMP_COLUMN)).collect()[0][0]

#     timestamps_backfill_df = timestamps_backfill_df.filter(f.col(TIMESTAMP_COLUMN) != max_timestamp)

#     timestamps_backfill_list = [row[TIMESTAMP_COLUMN] for row in timestamps_backfill_df.collect()]

#     return timestamps_backfill_list


def get_timestamps_to_backfill(config, table):
    backfill_to = check_widget_existance("backfill_to")
    catalog = config.get_catalog()
    entity = config.get_entity()
    database = config.get_database_for_entity(entity)

    timestamps_backfill_df = (
        spark.read.table(f"{catalog}.{database}.{table}")
        .select(f.col(TIMESTAMP_COLUMN).cast("string"))
        .distinct()
        .orderBy(f.desc(TIMESTAMP_COLUMN))
    )

    if backfill_to and backfill_to != "full":
        backfill_to = backfill_to.strip()

        timestamps_backfill_df = timestamps_backfill_df.filter(f.col(TIMESTAMP_COLUMN) >= backfill_to)

    max_timestamp = timestamps_backfill_df.agg(f.max(TIMESTAMP_COLUMN)).collect()[0][0]

    timestamps_backfill_df = timestamps_backfill_df.filter(f.col(TIMESTAMP_COLUMN) != max_timestamp)

    timestamps_backfill_list = [row[TIMESTAMP_COLUMN] for row in timestamps_backfill_df.collect()]

    return timestamps_backfill_list


def parse_custom_features_backfill(custom_features_backfill):
    parsed_results = []

    for entry in custom_features_backfill:
        features_list = entry["features"]
        timestamps = entry["timestamps"]

        parsed_features = ",".join(f"[{feature['prefix']}] {feature['notebook_name']}" for feature in features_list)

        parsed_feature_columns = [
            f"{feature['prefix']}_{col}"
            for feature in features_list
            for col in (
                feature["feature_columns"]
                if isinstance(feature["feature_columns"], list)
                else [feature["feature_columns"]]
            )
        ]

        parsed_results.append(
            {
                "parsed_features": (parsed_features, ",".join(parsed_feature_columns)),
                "timestamps": timestamps,
            }
        )

    return parsed_results


def parse_str_to_list(input_str):
    list_of_strings = input_str.split(",")

    return list_of_strings


# pylint: disable=too-many-statements
def add_backfilled_info_to_metadata(config, feature_columns):
    metadata_path = config.get_metadata_table()
    metadata_df = spark.read.table(metadata_path)

    feature_cols_list = parse_str_to_list(feature_columns)
    metadata_df_missing_backfill = metadata_df.filter(f.col("feature").isin(feature_cols_list))

    metadata_df_missing_backfill = metadata_df_missing_backfill.withColumn("backfilled", f.lit("Y"))

    delta_table = DeltaTable.forName(SparkSession.getActiveSession(), metadata_path)
    metadata_pk_columns = get_metadata_pk_columns()
    update_set = {"backfilled": "source.backfilled"}
    merge_condition = " AND ".join(f"target.{col.name} = source.{col.name}" for col in metadata_pk_columns)

    (
        delta_table.alias("target")
        .merge(metadata_df_missing_backfill.alias("source"), merge_condition)
        .whenMatchedUpdate(set=update_set)
        .execute()
    )


# pylint: disable=too-many-statements, too-many-branches
def validate_custom_features_backfill(custom_features_backfill: Any) -> bool:
    """
    Validate that the custom_features_backfill variable is in the correct format.

    Parameters:
    -----------
    custom_features_backfill : Any
        The variable to be validated.

    Returns:
    --------
    bool
        True if the variable is in the correct format, raises ValueError otherwise.

    Raises:
    -------
    ValueError
        If the custom_features_backfill variable is not in the correct format.
    """
    if not isinstance(custom_features_backfill, list):
        raise ValueError("custom_features_backfill must be a list.")
    # pylint: disable=too-many-nested-blocks
    for item in custom_features_backfill:
        if not isinstance(item, dict):
            raise ValueError("Each item in custom_features_backfill must be a dictionary.")

        if "features" not in item or "timestamps" not in item:
            raise ValueError("Each dictionary must contain 'features' and 'timestamps' keys.")

        if not isinstance(item["features"], list):
            raise ValueError("'features' must be a list of dictionaries.")

        for feature in item["features"]:
            if not isinstance(feature, dict):
                raise ValueError("Each feature must be a dictionary.")

            required_keys = {"prefix", "notebook_name", "feature_columns"}
            feature_keys = set(feature.keys())
            if not required_keys.issubset(feature_keys):
                raise ValueError(
                    f"Each feature dictionary must contain 'prefix', 'notebook_name', and 'feature_columns' keys. Found keys: {feature_keys}"
                )

            if not isinstance(feature["prefix"], str) or not isinstance(feature["notebook_name"], str):
                raise ValueError("'prefix' and 'notebook_name' values must be strings.")

            if not isinstance(feature["feature_columns"], (str, list)):
                raise ValueError("'feature_columns' value must be a string or a list of strings.")

            if isinstance(feature["feature_columns"], list) and not all(
                isinstance(col, str) for col in feature["feature_columns"]
            ):
                raise ValueError("All elements in 'feature_columns' list must be strings.")

        if not isinstance(item["timestamps"], list):
            raise ValueError("'timestamps' must be a list of strings.")

        for timestamp in item["timestamps"]:
            if not isinstance(timestamp, str):
                raise ValueError("Each timestamp must be a string.")

    return True


def log_feature_status():
    logger.info("Feature status: no features require backfill")


def process_custom_features_parameter(custom_features_backfill):
    try:
        validate_custom_features_backfill(custom_features_backfill)

        processed_features = parse_custom_features_backfill(custom_features_backfill)

        return processed_features
    # pylint: disable=try-except-raise
    except ValueError:
        raise


def backfill_pipeline(config, timestamps, feature_notebooks, feature_columns):
    backfill(timestamps, features=feature_notebooks, feature_columns=feature_columns)

    add_backfilled_info_to_metadata(config, feature_columns=feature_columns)


def backfill_added_features(custom_features_backfill=None):
    config = Config.load_feature_factory_config()

    # CUSTOM PART
    # user wants to define custom timestamps and features to backfill
    if custom_features_backfill:
        processed_custom_backfill = process_custom_features_parameter(custom_features_backfill)

        for feature_setting in processed_custom_backfill:
            timestamps = feature_setting["timestamps"]
            feature_notebooks, feature_columns = feature_setting["parsed_features"]
            backfill_pipeline(config, timestamps, feature_notebooks, feature_columns)
        return

    # AUTOMATED PART
    # Automatic backfill of all unbackfilled features for all timestamps
    features_table_dict = create_features_table_dict(config)

    # Check if there are features to backfill
    if features_table_dict:
        for table, (feature_notebooks, feature_columns) in features_table_dict.items():
            timestamps = get_timestamps_to_backfill(config, table)
            backfill_pipeline(config, timestamps, feature_notebooks, feature_columns)
    else:
        log_feature_status()
