import logging
import importlib
from typing import Optional

from shared.interfaces import BaseModule
logger = logging.getLogger("console")

class ModuleLoader:
    def __init__(
        self,
        modules: Optional[list[type[BaseModule]]] = None,
        modules_package_name: Optional[str] = None,
        ) -> None:

        if modules:
            logger.debug("Loading modules: %s", ", ".join(mod.__name__ for mod in modules))
            self._modules = self._initialization_module(modules)
        elif modules_package_name:
            logger.debug("Loading modules from package: %s", modules_package_name)
            try:
                package = importlib.import_module(modules_package_name)
            except ImportError as e:
                logger.critical("Failed import package '%s': %s", modules_package_name, e)
                raise

            exported_names = getattr(package, "__all__", None)
            if exported_names is None:
                logger.warning("Modules not found from package: %s", modules_package_name)
                self._modules = []
            else: 
                obj_list = []
                for name in exported_names:
                    try:
                        obj = getattr(package, name)
                        obj_list.append(obj)
                    except AttributeError:
                        logger.warning("Attribute '%s' listed in __all__ but not found in package '%s'", name, modules_package_name)
                        continue
                self._modules = self._initialization_module(obj_list)
        else:
            self._modules = []

    def _initialization_module(self, modules_obj: list[type[BaseModule]]) -> list[BaseModule]:
        good_modules: list[BaseModule] = []
        bad_modules: list[str] = []
        for module_cls in modules_obj:
            try:
                if isinstance(module_cls, type) and issubclass(module_cls, BaseModule) and module_cls is not BaseModule:
                    instance = module_cls()
                    good_modules.append(instance)
                else:
                    raise TypeError("Module not valid")
            except Exception as e:
                name = getattr(module_cls, "__name__", repr(module_cls))
                bad_modules.append(name)
                logger.warning("Module %s skipping: %s", name, e)
                continue

        if good_modules:
            logger.debug("Modules that will be loaded: %s", ", ".join(mod.name for mod in good_modules))
        else:
            logger.warning("Modules cannot be loaded")
        if bad_modules:
            logger.debug("Modules that were skipped: %s", bad_modules)
        return good_modules

    def get_moduls(self) -> list[BaseModule]:
        return self._modules