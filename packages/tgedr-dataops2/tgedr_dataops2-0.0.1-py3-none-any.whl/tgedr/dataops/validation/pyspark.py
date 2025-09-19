"""Data validation utilities for PySpark DataFrames using Great Expectations."""

from typing import Any

from great_expectations.dataset.sparkdf_dataset import SparkDFDataset

from tgedr.dataops.validation.abs import DataValidation


class Impl(DataValidation):
    """Implementation of DataValidation for PySpark DataFrames using Great Expectations."""

    def _get_dataset(self, df: Any) -> SparkDFDataset:
        return SparkDFDataset(df)
