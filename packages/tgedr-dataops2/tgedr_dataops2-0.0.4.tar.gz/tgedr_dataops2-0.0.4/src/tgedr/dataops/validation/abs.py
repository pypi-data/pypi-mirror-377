"""Abstract base classes and utilities for data validation using Great Expectations.

This module defines the DataValidation abstract base class, a custom exception for validation errors,
and a factory method for loading concrete validation implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from great_expectations.core import ExpectationSuite
from great_expectations.dataset import PandasDataset, SparkDFDataset
from tgedr.dataops.commons.utils_reflection import UtilsReflection

logger = logging.getLogger(__name__)


class DataValidationException(Exception):
    """Custom exception raised for data validation errors."""


class DataValidation(ABC):
    """Abstract base class for data validation using Great Expectations.

    Subclasses should implement the _get_dataset method to convert input data
    into a Great Expectations Dataset for validation.
    """

    @staticmethod
    def get_impl(name: str) -> "DataValidation":
        """Factory method to load and instantiate a concrete DataValidation implementation by name.

        Args:
            name (str): The name of the validation implementation to load.

        Returns:
            DataValidation: An instance of the requested DataValidation implementation.

        Raises:
            DataValidationException: If the implementation cannot be loaded.

        """
        logger.info(f"[get_impl|in] ({name})")
        result = None
        module = ".".join(__name__.split(".")[:-1]) + "." + name.lower()
        try:
            result = UtilsReflection.load_subclass_from_module(module, "Impl", DataValidation)()
        except Exception as x:  # noqa: BLE001
            raise DataValidationException(f"[get_impl] couldn't load implementation for {name}: {x}")  # noqa: B904
        logger.info(f"[get_impl|out] ({result})")
        return result

    @abstractmethod
    def _get_dataset(self, df: Any) -> PandasDataset | SparkDFDataset:
        raise NotImplementedError("DataValidation")  # noqa: EM101

    def validate(self, df: Any, expectations: dict) -> None:
        """Validate the given data against the provided expectations using Great Expectations.

        Args:
            df (Any): The input data to validate.
            expectations (dict): The expectations suite to validate against.

        Returns:
            dict: The validation result as a JSON-serializable dictionary.

        Raises:
            DataValidationException: If validation fails or an error occurs.

        """
        logger.info(f"[validate|in] ({df}, {expectations})")

        try:
            dataset = self._get_dataset(df)

            validation = dataset.validate(expectation_suite=ExpectationSuite(**expectations), only_return_failures=True)
            result = validation.to_json_dict()
        except Exception as x:  # noqa: BLE001 # pragma: no cover
            raise DataValidationException(f"[validate] failed data expectations", x)  # noqa: B904, F541 # pragma: no cover

        logger.info(f"[validate|out] => {result['success']}")
        return result
