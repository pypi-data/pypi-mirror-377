"""Persist pandas DataFrames as Excel files in Unity Catalog volumes.

Provides the PandasDf2ExcelVolumeSink class for saving pandas DataFrames as Excel files in Unity Catalog volumes.
"""

import logging
from typing import Any
import time
from pathlib import Path
from shutil import copyfile
import pandas as pd
from tgedr.dataops.sink.sink import SinkException
from tgedr.dataops.sink.catalog_sink import CatalogSink

logger = logging.getLogger(__name__)


class PandasDf2ExcelVolumeSink(CatalogSink):
    """Sink for persisting pandas DataFrames as Excel files in Unity Catalog volumes.

    This class provides methods to save a pandas DataFrame to an Excel file
    and copy it to a specified target location within Unity Catalog volumes.

    Attributes
    ----------
    CONTEXT_DF : str
        Key for the DataFrame in the context dictionary.
    CONTEXT_TARGET : str
        Key for the target file path in the context dictionary.
    __TMP_URL : str
        Temporary directory for storing intermediate Excel files.

    """

    CONTEXT_DF = "df"
    CONTEXT_TARGET = "target"
    __TMP_URL = "/local_disk0/tmp"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the PandasDf2ExcelVolumeSink with the given configuration."""
        CatalogSink.__init__(self, config=config)

    def put(self, context: dict | None = None) -> any:
        """Persist a pandas dataframe as an excel file in Unity Catalog volumes.

        Parameters
        ----------
        context : dict, optional
            A dictionary containing 'df' and 'target' paths.

        Raises
        ------
        SinkException
            If required context keys are missing.

        """
        logger.info(f"[put|in] ({context})")

        if self.CONTEXT_DF not in context:
            raise SinkException(f"[put] you must provide context for {self.CONTEXT_DF}")
        if self.CONTEXT_TARGET not in context:
            raise SinkException(f"[put] you must provide context for {self.CONTEXT_TARGET}")

        df: pd.DataFrame = context[self.CONTEXT_DF]
        if type(df) is not pd.core.frame.DataFrame:
            raise SinkException(f"[put] expected a pandas DataFrame, got: {type(df)}")

        target: str = context[self.CONTEXT_TARGET]

        # Ensure target parent directory exists
        target_path = Path(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_file = f"{self.__TMP_URL}/{int(time.time_ns())}.xlsx"
        df.to_excel(
            tmp_file,
            sheet_name="Sheet1",  # Name of the sheet
            index=False,  # Don't include row indices
            header=True,  # Include column headers
            engine="openpyxl",  # Excel engine to use
        )
        copyfile(tmp_file, target)
        logger.info("[put|out]")
