from glob import glob
from http.client import NOT_IMPLEMENTED
from importlib import import_module
from ..loggers import logger


class BaseImportService:
    """
    This class imports items from each folder
    that named "target_subfolders" recursively in the TARGET_FOLDER.
    It looks into __init__.py and gets __all__ variable.
    Thus all folders from which items have to be imported
    should have __init__.py file with __all__ variable.
    """
    TARGET_FOLDER = "apps"
    TARGET_SUBFOLDERS = NOT_IMPLEMENTED
    NOT_CHECKED_MESSAGE = "is not checked for items"

    @classmethod
    def _get_module_items(cls, module_name) -> list[dict]:
        """
        import classes / methods / variables module in specific app
        and get __all__ variable to get these items in output format:
        [{"name": item_name, "value": exact_class_or_method}]
        """
        module_name = module_name[:-1]
        module_name = module_name.replace("/", ".")
        target_module = import_module(module_name)
        module_items = [{"name": item_name, "value": getattr(target_module, item_name)}
                        for item_name in target_module.__all__]
        return module_items

    @classmethod
    def _get_modules_with_items(cls, target_subfolders=None) -> list[str]:
        """
        Scan all "target_subfolders" folders in TARGET_FOLDER recursively
        """
        subfolders = target_subfolders or cls.TARGET_SUBFOLDERS

        return glob(f'{cls.TARGET_FOLDER}/**/{subfolders}/', recursive=True)

    @classmethod
    def get_items(cls, target_subfolders=None, not_checked_message=None) -> list[dict]:
        """
        Main method of the class that returns the list of dicts of imported items
        in format [{"name": item_name, "value": exact_class_or_method}]
        """
        items = []
        modules_with_items = cls._get_modules_with_items(target_subfolders)
        not_checked_message = not_checked_message or cls.NOT_CHECKED_MESSAGE

        for module_path in modules_with_items:
            try:
                items += cls._get_module_items(module_path)
            except Exception:
                logger.info(f"App {module_path} {not_checked_message}")
        return items
