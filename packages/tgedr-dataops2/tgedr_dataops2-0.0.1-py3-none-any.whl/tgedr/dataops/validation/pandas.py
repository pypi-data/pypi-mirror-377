"""Module for Pandas-based data validation using Great Expectations."""

from typing import Any

import great_expectations as ge
from great_expectations.dataset.sparkdf_dataset import PandasDataset

from tgedr.dataops.validation.abs import DataValidation


class Impl(DataValidation):
    """Implementation of DataValidation using PandasDataset for data validation."""

    def _get_dataset(self, df: Any) -> PandasDataset:
        return ge.from_pandas(df)
