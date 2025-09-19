"""Module for persisting objects/files to Unity Catalog volumes using Databricks utilities."""

import logging

from tgedr.dataops.commons.utils_databricks import UtilsDatabricks
from tgedr.dataops.sink.sink import Sink, SinkException

logger = logging.getLogger(__name__)


class CatalogSink(Sink):
    """sink class used to save/persist an object/file to unitty catalog volumes."""

    CONTEXT_SOURCE_PATH = "source"
    CONTEXT_TARGET_PATH = "target"

    def __init__(self, config: dict | None = None) -> None:
        """Initialize CatalogSink with optional configuration."""
        Sink.__init__(self, config=config)
        self.__dbutils = None

    @property
    def _dbutils(self) -> any:
        if self.__dbutils is None:
            self.__dbutils = UtilsDatabricks.get_dbutils()
        return self.__dbutils

    def put(self, context: dict | None = None) -> any:
        """Persist an object or file from the source path to the target path in Unity Catalog volumes.

        Parameters
        ----------
        context : dict, optional
            A dictionary containing 'source' and 'target' paths.

        Raises
        ------
        SinkException
            If required context keys are missing.

        """
        logger.info(f"[put|in] ({context})")

        if self.CONTEXT_SOURCE_PATH not in context:
            raise SinkException(f"you must provide context for {self.CONTEXT_SOURCE_PATH}")  # pragma: no cover
        if self.CONTEXT_TARGET_PATH not in context:
            raise SinkException(f"you must provide context for {self.CONTEXT_TARGET_PATH}")  # pragma: no cover

        source = context[self.CONTEXT_SOURCE_PATH]
        target = context[self.CONTEXT_TARGET_PATH]

        self._dbutils.fs.cp(source, target)
        logger.info("[put|out]")

    def delete(self, context: dict | None = None) -> None:
        """Delete the object or file at the target path in Unity Catalog volumes.

        Parameters
        ----------
        context : dict, optional
            A dictionary containing the 'target' path.

        Raises
        ------
        SinkException
            If the required context key is missing or the target is not found.

        """
        logger.info(f"[delete|in] ({context})")

        if self.CONTEXT_TARGET_PATH not in context:
            raise SinkException(f"you must provide context for {self.CONTEXT_TARGET_PATH}")  # pragma: no cover

        target = context[self.CONTEXT_TARGET_PATH]
        if 0 < len(self._dbutils.fs.ls(target)):
            self._dbutils.fs.rm(target, True)  # noqa: FBT003
        else:
            raise SinkException(f"[delete] is it a dir or a folder? {target}")  # pragma: no cover

        logger.info("[delete|out]")
