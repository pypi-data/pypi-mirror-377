"""Utility functions and classes for working with Apache Spark.

This module provides:
- UtilsSpark: a class with handy functions to work with Spark sessions and schemas.
"""

import logging
import os
import sys
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class UtilsSpark:
    """class with handy functions to work with spark."""

    ENV_KEY_PYSPARK_LOCAL = "PYSPARK_LOCAL"

    @staticmethod
    def get_local_spark_session(config: dict | None = None) -> SparkSession:
        """Create and return a local SparkSession configured for Delta Lake.

        Parameters
        ----------
        config : dict, optional
            Additional Spark configuration options.

        Returns
        -------
        SparkSession
            A configured local SparkSession instance.

        """
        logger.debug(f"[get_local_spark_session|in] ({config})")
        os.environ["PYSPARK_SUBMIT_ARGS"] = (
            "--packages io.delta:delta-spark_2.12:3.3.0,io.delta:delta-storage:3.3.0 pyspark-shell"
        )
        os.environ["PYSPARK_PYTHON"] = sys.executable
        os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
        builder = (
            SparkSession.builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.driver.host", "localhost")
        )

        if config is not None:
            for k, v in config.items():
                builder.config(k, v)

        spark = builder.getOrCreate()
        logger.info(f"[get_local_spark_session|out] => {spark}")
        return spark

    @staticmethod
    def get_spark_session(config: dict | None = None) -> SparkSession:
        """Get or create a SparkSession, using local mode if the PYSPARK_LOCAL environment variable is set.

        Parameters
        ----------
        config : dict, optional
            Additional Spark configuration options.

        Returns
        -------
        SparkSession
            A configured SparkSession instance.

        """
        logger.debug(f"[get_spark_session|in] ({config})")

        if "1" == os.getenv(UtilsSpark.ENV_KEY_PYSPARK_LOCAL):
            spark: SparkSession = UtilsSpark.get_local_spark_session(config)
        else:
            logger.info("[get_spark_session] no active session, creating a new one")
            spark_config: dict = {
                "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
                "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            }
            if config is not None:
                spark_config.update(config)

            builder = SparkSession.builder
            for k, v in spark_config.items():
                builder.config(k, v)
            spark: SparkSession = builder.getOrCreate()

        logger.debug(f"[get_spark_session|out] => {spark}")
        return spark
