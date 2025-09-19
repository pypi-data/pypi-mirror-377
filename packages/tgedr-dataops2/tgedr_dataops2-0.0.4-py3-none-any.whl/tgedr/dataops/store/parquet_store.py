"""Provides the ParquetStore class for interacting with Parquet files using a filesystem interface."""

import logging
from abc import ABC
import pandas as pd
from pathlib import Path
from pyarrow import fs
from pyarrow.fs import FileInfo, FileType
from tgedr.dataops.store.store import Store


logger = logging.getLogger(__name__)


class ParquetStore(Store, ABC):
    """ParquetStore provides methods to interact with Parquet files using a filesystem interface."""

    __PARQUET_ENGINE = "pyarrow"

    def _ensure_key_parent(self, key: str) -> None:
        """Ensure that the directory(parent) for the given key exists.

        Args:
            key (str): The file path or identifier for the Parquet file.

        """
        logger.info(f"[_ensure_key_parent|in] ({key})")

        parent = str(Path(key).parent)
        info: FileInfo = self._fs.get_file_info(parent)
        if info.type != FileType.Directory:
            self._fs.create_dir(parent, recursive=True)
            logger.info(f"[_ensure_key_parent] created key parent: {parent}")
        else:
            logger.info(f"[_ensure_key_parent] key parent already exists: {parent}")
        logger.info("[_ensure_key_parent|out]")

    def __init__(self, config: dict[str, int | str | float] | None = None) -> None:
        """Initialize the ParquetStore with an optional configuration dictionary.

        Args:
            config (dict[str, Any] | None): Optional configuration for the store.

        """
        self._config = config
        self._fs = fs.LocalFileSystem()

    def get(self, key: str, cols: list[str] | None = None, **kwargs) -> pd.DataFrame:
        """Retrieve a DataFrame from a Parquet file specified by the given key.

        Args:
            key (str): The file path or identifier for the Parquet file.
            cols (list or None): Optional list of column names to read from the Parquet file.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame: The loaded DataFrame from the Parquet file.

        """
        logger.info(f"[get|in] ({key}, {cols}, {kwargs})")
        result = pd.read_parquet(key, engine=self.__PARQUET_ENGINE, columns=cols)
        logger.info(f"[get|out] => {result}")
        return result

    def delete(self, key: str, **kwargs) -> None:
        """Delete a Parquet file or directory specified by the given key.

        Args:
            key (str): The file path or identifier for the Parquet file or directory.
            **kwargs: Additional keyword arguments.

        """
        logger.info(f"[delete|in] ({key}, {kwargs})")
        info = self._fs.get_file_info(key).type.name
        if info != "NotFound":
            if self._fs.get_file_info(key).type.name == "Directory":
                self._fs.delete_dir(key)
            else:
                self._fs.delete_file(key)
        logger.info("[delete|out]")

    def save(self, df: pd.DataFrame, key: str, partition_fields: list[str] | None = None, **kwargs) -> None:
        """Save a DataFrame to a Parquet file, optionally partitioned by specified fields.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            key (str): The file path or identifier for the Parquet file.
            partition_fields (list[str] | None): Optional list of fields to partition by.
            **kwargs: Additional keyword arguments.

        """
        logger.info(f"[save|in] ({df}, {key}, {partition_fields}, {kwargs})")
        self.delete(key)
        self._ensure_key_parent(key)
        df.to_parquet(key, index=False, partition_cols=partition_fields, engine=self.__PARQUET_ENGINE)
        logger.info("[save|out]")

    def update(
        self, df: pd.DataFrame, key: str, key_fields: list[str], partition_fields: list[str] | None = None, **kwargs
    ) -> None:
        """Update an existing Parquet file by merging the provided DataFrame with the existing data based on key fields.

        Args:
            df (pd.DataFrame): The DataFrame containing new or updated data.
            key (str): The file path or identifier for the Parquet file.
            key_fields (list[str]): List of fields to use as keys for merging/updating.
            partition_fields (list[str] | None): Optional list of fields to partition by.
            schema (Any): Optional schema information.
            **kwargs: Additional keyword arguments.

        """
        logger.info(f"[update|in] ({df}, {key}, {key_fields}, {partition_fields}, {kwargs})")

        df0 = self.get(key)
        match = pd.merge(df0.reset_index(), df.reset_index(), on=key_fields)  # noqa: PD015
        index_left = match["index_x"]
        index_right = match["index_y"]
        df0.iloc[index_left] = df.iloc[index_right]
        self.save(df0, key, partition_fields=partition_fields)
        logger.info("[update|out]")
