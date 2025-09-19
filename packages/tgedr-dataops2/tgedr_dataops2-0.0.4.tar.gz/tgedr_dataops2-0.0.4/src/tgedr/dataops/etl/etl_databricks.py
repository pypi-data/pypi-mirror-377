"""ETL module for Databricks integration.

This module provides the EtlDatabricks class, which extends the base ETL functionality
to support Databricks-specific features such as task value sharing and run ID management.
"""

import inspect
import logging
import re
from typing import Any

from tgedr.dataops.commons.utils_databricks import UtilsDatabricks
from tgedr.dataops.etl.etl import Etl, EtlException

logger = logging.getLogger(__name__)


class EtlDatabricks(Etl):
    """ETL class for Databricks integration.

    Extends the base ETL functionality to support Databricks-specific features such as
    task value sharing and run ID management.
    """

    _CONFIG_KEY_RUN_ID = "run_id"
    _NO_RUN_ID = "0"

    def __init__(self, configuration: dict[str, Any] | None = None) -> None:
        """Initialize the EtlDatabricks instance.

        Args:
            configuration (dict[str, Any] | None): Optional configuration dictionary.
                Should contain 'run_id' when running in Databricks.

        """
        super().__init__(configuration=configuration)
        # when running in databricks we should always pass `run_id` to the etl: `run_id: {{job.run_id}}`
        self._run_id: str = (
            configuration[self._CONFIG_KEY_RUN_ID]
            if configuration and self._CONFIG_KEY_RUN_ID in configuration
            else self._NO_RUN_ID
        )

    def run(self) -> Any:
        """Execute the ETL process: extract, validate, transform, validate, and load data.

        Returns:
            Any: The result of the load operation, typically a dictionary of result values or None.

        """
        logger.info("[run|in]")

        self.extract()
        self.validate_extract()

        self.transform()
        self.validate_transform()

        # load might return a dictionary of result values
        result: dict[str, str] = self.load()

        if (result is not None) and (self._NO_RUN_ID != self._run_id):
            # if we are running in databricks, we will set the result values
            dbutils = UtilsDatabricks.get_dbutils()
            for key in result:  # noqa: PLC0206
                dbutils.jobs.taskValues.set(key=key, value=result[key])

        logger.info(f"[run|out] => {result}")
        return result

    def read_task_value(self, key) -> str:  # noqa: ANN001
        """Read values from a task.

        task values can be shared among the tasks using the following convention:
        <task_key>__<key> (ex: FindMissingPeriods__fileset_periods)
        this function allows us to read those values
        """
        logger.info(f"[read_task_value|in] ({key})")
        dbutils = UtilsDatabricks.get_dbutils()

        keys: list[str] = key.split("__")
        result = dbutils.jobs.taskValues.get(taskKey=keys[0], key=keys[1])
        logger.info(f"[read_task_value|out] => {result}")
        return result

    @staticmethod
    def inject_configuration(f):  # noqa: ANN001, ANN205, D102
        def decorator(self):  # noqa: ANN001, ANN202
            signature = inspect.signature(f)

            # related to task values convention (see below)
            task_value_param_pattern = re.compile(r"\w+__\w+")

            missing_params = []
            params = {}
            # check every argument in the function signature
            for param in [parameter for parameter in signature.parameters if parameter != "self"]:
                # if there is a configuration for the argument
                # we will use it
                if self._configuration is not None and param in self._configuration:
                    params[param] = self._configuration[param]
                else:  # noqa: PLR5501
                    # if it has a default value, we will use it
                    if signature.parameters[param].default != inspect._empty:  # noqa: SLF001
                        params[param] = signature.parameters[param].default
                    else:  # noqa: PLR5501
                        # if no configuration or default value are provided then check if this is a task value:
                        #
                        # CONVENTION: read values from previous task values when running in databricks,
                        # we are assuming params with a namespace prefixed with two underscores
                        # (e.g.: `namespace__param`) to be task values depicting `task_key__key`
                        if (self._NO_RUN_ID != self._run_id) and (task_value_param_pattern.match(param) is not None):
                            params[param] = self.read_task_value(param)

                # if no value found at this stage, we will mark it as `missing`
                if param not in params:
                    missing_params.append(param)

            if 0 < len(missing_params):
                raise EtlException(
                    f"{type(self).__name__}.{f.__name__}: missing required configuration parameters: {missing_params}"
                )

            return f(
                self,
                *[params[argument] for argument in params],
            )

        return decorator
