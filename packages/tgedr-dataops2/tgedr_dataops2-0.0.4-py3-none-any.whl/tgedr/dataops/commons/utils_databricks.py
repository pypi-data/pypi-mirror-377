"""Utility functions for interacting with Databricks and managing Databricks-related operations.

This module provides helpers for obtaining dbutils, extracting run context, and logging within Databricks environments.
"""

import json
import logging

from pyspark.sql import SparkSession

from tgedr.dataops.commons.utils_spark import UtilsSpark

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


class UtilsDatabricks:
    """Utility class for interacting with Databricks.

    Provides methods to obtain dbutils, extract run context, and manage Databricks-related operations.
    """

    __DATABRICKS_VERSION_THRESHOLD = 7.3
    __DATABRICKS_UTILS = None

    @staticmethod
    def get_dbutils() -> object:
        """Helper method to load Azure Databricks dbutils instance.

        Accordingly to Microsoft documentation:
        https://docs.microsoft.com/en-us/azure/databricks/dev-tools/databricks-connect#access-dbutils
        """
        logger.debug("[UtilsDatabricks.get_dbutils|in]")

        spark: SparkSession = UtilsSpark.get_spark_session()

        dbutils = None
        if not UtilsDatabricks.__DATABRICKS_UTILS:
            # we are going to diplomatically try to get some info from spark, avoiding the need for a fight here
            databricks_runtime_version = None
            try:
                databricks_runtime_version = float(spark.conf.get("spark.databricks.clusterUsageTags.sparkVersion")[:3])
            except Exception as x:  # noqa: BLE001 # pragma: no cover
                logger.info(
                    "[UtilsDatabricks.get_dbutils] could not get sparkVersion from spark conf", exc_info=x
                )  # pragma: no cover

            service_client_enabled = "false"
            try:
                service_client_enabled = spark.conf.get("spark.databricks.service.client.enabled")
            except Exception as x:  # noqa: BLE001
                logger.info(
                    "[UtilsDatabricks.get_dbutils] could not get service_client_enabled from spark conf", exc_info=x
                )

            logger.debug(f"[UtilsDatabricks.get_dbutils] databricksRuntimeVersion: {databricks_runtime_version}")
            try:
                if (
                    databricks_runtime_version is not None
                    and databricks_runtime_version >= UtilsDatabricks.__DATABRICKS_VERSION_THRESHOLD
                ) or (service_client_enabled == "true"):
                    from pyspark.dbutils import DBUtils  # type: ignore  # noqa: PGH003

                    dbutils = DBUtils(spark)
                    logger.debug("[UtilsDatabricks.get_dbutils] got it from spark")
                else:
                    import IPython  # pragma: no cover

                    # pragma: no cover
                    dbutils = IPython.get_ipython().user_ns["dbutils"]  # pragma: no cover
                    logger.debug("[UtilsDatabricks.get_dbutils] got it from IPython")  # pragma: no cover

                UtilsDatabricks.__DATABRICKS_UTILS = dbutils
            except Exception as x:  # noqa: BLE001 # pragma: no cover
                logger.debug("[UtilsDatabricks.get_dbutils] could not get it", exc_info=x)  # pragma: no cover
        else:
            dbutils = UtilsDatabricks.__DATABRICKS_UTILS

        logger.debug(f"[UtilsDatabricks.get_dbutils|out] => {dbutils}")
        return dbutils

    @staticmethod
    def get_run_context():  # noqa: ANN205, D102
        logger.info("[UtilsDatabricks.get_run_context|in]")
        dbutils = UtilsDatabricks.get_dbutils()

        def get_widget_value(key, default_value=None):  # noqa: ANN001, ANN202
            try:
                return dbutils.widgets.get(key)
            except Exception:  # noqa: BLE001 # pragma: no cover
                return default_value  # pragma: no cover

        logger.info(f"[UtilsDatabricks.get_run_context] getAll: {dbutils.widgets.getAll()}")

        result = {}
        result["module_name"] = get_widget_value("module")
        result["callable_name"] = get_widget_value("callable")
        result["params"] = get_widget_value("params")

        context_str = dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson()
        databricks_context = json.loads(context_str)
        result["databricks_context"] = databricks_context
        tags_section = databricks_context.get("tags", {})
        result["job_run_id"] = tags_section.get("runId", None) if tags_section else None
        result["job_id"] = tags_section.get("jobId", None) if tags_section else None

        logger.info(f"[UtilsDatabricks.get_run_context|out] => {result}")
        return result
