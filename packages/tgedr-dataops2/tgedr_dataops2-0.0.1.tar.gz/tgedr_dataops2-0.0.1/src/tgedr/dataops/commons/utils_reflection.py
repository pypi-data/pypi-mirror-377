"""Utility module providing reflection-based functionality for Python classes and modules.

Includes tools for dynamic class loading, type checking, and package inspection.
"""

import importlib
import inspect
import logging
import os
import sys
from importlib import import_module
from typing import Any

logger = logging.getLogger(__name__)


class UtilsReflection:
    """Utility class providing reflection-based operations for Python classes and modules.

    This class contains static methods for dynamic class loading, type checking,
    package inspection, and finding class implementations across packages.
    """

    __MODULE_EXTENSIONS = (".py", ".pyc", ".pyo")

    @staticmethod
    def load_class(clazz: str, parent_check: type | None = None) -> Any:
        """Load a class dynamically from a string representation of its full path.

        Args:
            clazz (str): Fully qualified class name (e.g., 'package.module.ClassName')
            parent_check (type|None, optional): Parent class to verify inheritance from. Defaults to None.

        Returns:
            Any: The loaded class object

        Raises:
            TypeError: If the loaded object is not callable or doesn't inherit from parent_check

        """
        logger.debug(f"[load_class|in] (clazz={clazz}, parent_check={parent_check})")
        type_elements = clazz.split(".")
        module = ".".join(type_elements[:-1])
        _clazz = type_elements[-1]

        result = getattr(import_module(module), _clazz)

        if not callable(result):
            raise TypeError(f"Object {_clazz} in {module} is not callable.")

        if parent_check and (not issubclass(result, parent_check)):
            raise TypeError(f"Wrong class type, it is not a subclass of {parent_check.__name__}")

        logger.debug(f"[load_class|out] => {result}")
        return result

    @staticmethod
    def load_subclass_from_module(module: str, clazz: str, super_clazz: type) -> Any:
        """Load a class from a specified module and verify it's a subclass of the given super class.

        Args:
            module (str): The name of the module containing the class
            clazz (str): The name of the class to load
            super_clazz (type): The superclass that the loaded class must inherit from

        Returns:
            Any: The loaded class object

        Raises:
            TypeError: If the loaded object is not callable or not a subclass of super_clazz

        """
        logger.info(f"[load_subclass_from_module|in] (module={module}, clazz={clazz}, super_clazz={super_clazz})")
        result = getattr(import_module(module), clazz)

        if not callable(result):
            raise TypeError(f"Object {clazz} in {module} is not callable.")

        if super_clazz and (not issubclass(result, super_clazz)):
            raise TypeError(f"Wrong class type, it is not a subclass of {super_clazz.__name__}")

        logger.info(f"[load_subclass_from_module|out] => {result}")
        return result

    @staticmethod
    def get_type(module: str, _type: str) -> type:
        """Get a type object from a specified module.

        Args:
            module (str): The name of the module containing the type
            _type (str): The name of the type to get

        Returns:
            type: The type object from the specified module

        """
        logger.info(f"[get_type|in] (module={module}, _type={_type})")
        result = None

        result = getattr(import_module(module), _type)

        logger.info(f"[get_type|out] => {result}")
        return result

    @staticmethod
    def is_subclass_of(sub_class: type, super_class: type) -> bool:
        """Check if a class is a subclass of another class.

        Args:
            sub_class (type): The class to check
            super_class (type): The potential parent class

        Returns:
            bool: True if sub_class is a subclass of super_class, False otherwise

        """
        logger.info(f"[is_subclass_of|in] ({sub_class}, {super_class})")
        result = False

        if callable(sub_class) and issubclass(sub_class, super_class):
            result = True

        logger.info(f"[is_subclass_of|out] => {result}")
        return result

    @staticmethod
    def find_module_classes(module: str) -> list[Any]:
        """Find all classes defined in a specified module.

        Args:
            module (str): The name of the module to search in

        Returns:
            list[Any]: List of class objects found in the module

        """
        logger.info(f"[find_module_classes|in] ({module})")
        result = []
        for _, obj in inspect.getmembers(sys.modules[module]):
            if inspect.isclass(obj):
                result.append(obj)
        logger.info(f"[find_module_classes|out] => {result}")
        return result

    @staticmethod
    def find_class_implementations_in_package(package_name: str, super_class: type) -> dict[str, type]:
        """Find all implementations of a superclass within a specified package.

        Args:
            package_name (str): The name of the package to search in
            super_class (type): The superclass to find implementations of

        Returns:
            dict[str, type]: Dictionary mapping module names to their implementation classes

        """
        logger.info(f"[find_class_implementations_in_package|in] ({package_name}, {super_class})")
        result = {}

        the_package = importlib.import_module(package_name)
        pkg_path = the_package.__path__[0]
        modules = [
            package_name + "." + module.split(".")[0]
            for module in os.listdir(pkg_path)
            if module.endswith(UtilsReflection.__MODULE_EXTENSIONS) and module != "__init__.py"
        ]

        logger.info(f"[find_class_implementations_in_package] found modules: {modules}")

        for _module in modules:
            if _module not in sys.modules:
                importlib.import_module(_module)

            for _class in UtilsReflection.find_module_classes(_module):
                if UtilsReflection.is_subclass_of(_class, super_class) and _class != super_class:
                    result[_module] = _class

        logger.info(f"[find_class_implementations_in_package|out] => {result}")
        return result

    @staticmethod
    def find_package_path(package_name: str) -> str:
        """Find the filesystem path for a given Python package.

        Args:
            package_name (str): The name of the package to locate

        Returns:
            str: The absolute filesystem path where the package is installed

        """
        logger.info(f"[find_package_path|in] ({package_name})")
        the_package = importlib.import_module(package_name)
        result = the_package.__path__[0]
        logger.info(f"[find_package_path|out] => {result}")
        return result

    @staticmethod
    def find_class_implementations(packages: str, clazz: Any) -> dict[str, Any]:
        """Find all class implementations of a given class in specified packages.

        Args:
            packages (str): Comma-separated list of package names to search in
            clazz (Any): The base class to find implementations of

        Returns:
            dict[str, Any]: Dictionary mapping implementation names to their class objects

        """
        logger.info(f"[find_class_implementations|in] ({packages}, {clazz})")
        result = {}
        _packages = [a.strip() for a in packages.split(",")]

        # find classes that extend clazz
        for pack_name in _packages:
            module_class_map = UtilsReflection.find_class_implementations_in_package(pack_name, clazz)
            for mod, _clazz in module_class_map.items():
                impl = mod.split(".")[-1]
                result[impl] = _clazz

        logger.info(f"[find_class_implementations|out] => {result}")
        return result

    @staticmethod
    def is_module(module: str) -> bool:
        """Check if a given module name exists and can be imported.

        Args:
            module (str): The name of the module to check

        Returns:
            bool: True if the module exists and can be imported, False otherwise

        """
        logger.info(f"[is_module|in] ({module})")
        result = False
        try:
            import_module(module)
            result = True
        except ModuleNotFoundError:
            logger.exception(f"[is_module] Module {module} could not be imported.")

        logger.info(f"[is_module|out] => {result}")
        return result

    @staticmethod
    def is_function(f: str) -> bool:
        """Check if a given string represents a valid function in a module.

        Args:
            f (str): The function name to check in format 'module.function_name'

        Returns:
            bool: True if the name represents a valid function, False otherwise

        Raises:
            ValueError: If the function name is not in the correct format

        """
        logger.info(f"[is_function|in] ({f})")
        result = False
        parts: list = f.rsplit(".", 1)
        if len(parts) != 2:
            msg = "[is_function] function name must be in the format 'module.function_name'"
            raise ValueError(msg)

        try:
            module, function_name = parts
            result = type(UtilsReflection.get_type(module, function_name)).__name__ == "function"
        except Exception as e:
            logger.exception(f"[is_function] {f} is not a function", exc_info=e)

        logger.info(f"[is_function|out] => {result}")
        return result
