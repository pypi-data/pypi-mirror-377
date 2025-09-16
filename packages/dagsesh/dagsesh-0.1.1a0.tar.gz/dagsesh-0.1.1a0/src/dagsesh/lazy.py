"""Delay imports of Python modules and packages."""

import importlib
import types


class Loader(types.ModuleType):
    """Lazily import a module."""

    def __init__(self, local_name: str, parent_module_globals: dict, module_name: str):
        """Initialise a lazy importer for a module.

        This class enables deferred loading of a module until its first use,
        improving startup performance by avoiding immediate imports.

        Parameters:
            local_name: The name under which the imported module will be accessible
                within the local namespace.
            parent_module_globals: The globals dictionary of the parent module where
                the lazy import will be registered.
            module_name: The name of the module to be lazily imported.

        """
        self.__local_name = local_name
        self.__parent_module_globals = parent_module_globals

        super().__init__(module_name)

    @property
    def local_name(self) -> str:
        """Get the local_name."""
        return self.__local_name

    @property
    def parent_module_globals(self) -> dict:
        """Get the parent_module_globals."""
        return self.__parent_module_globals

    def _load(self) -> types.ModuleType:
        """Import the target module and insert it into the parent's namespace.

        The method will update this object's dict so that if someone keeps a reference to the
        LazyLoader, lookups are efficient (__getattr__ is only called on lookups that fail).

        Returns:
            Python module.

        """
        module = importlib.import_module(self.__name__)
        self.parent_module_globals[self.local_name] = module

        self.__dict__.update(module.__dict__)

        return module

    def __getattr__(self, item: str) -> str:
        """Delegate attribute access to the lazily loaded module.

        This method is called when an attribute not found in the instance is accessed.
        It triggers the lazy loading of the module and then attempts to retrieve
        the requested attribute from it.

        Parameters:
            item: The name of the attribute to retrieve from the loaded module.

        Returns:
            The value of the requested attribute from the underlying module.

        Raises:
            AttributeError: If the attribute does not exist in the loaded module.

        """
        module = self._load()

        return getattr(module, item)
