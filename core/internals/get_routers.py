from glob import glob
from importlib import import_module
from ..loggers import logger


class GetRouters:
    TARGET_FOLDER = "apps"

    @classmethod
    def _get_routers_data(cls, module_name):
        # import models module in specific app
        # and get __all__ variable to get model for generating
        # migrations
        module_name = module_name.replace("/", ".").replace(".py", "")
        models_module = import_module(module_name)
        return getattr(models_module, "routers")

    @classmethod
    def call(cls, version):
        # scan all 'models' folders in TARGET_FOLDER recursively
        routers_data = []
        files_with_routers = glob(
            f'{cls.TARGET_FOLDER}/**/routers_{version}.py', recursive=True)

        for module_path in files_with_routers:
            try:
                routers_data += cls._get_routers_data(module_path)
            except Exception as e:
                logger.info(f"App {module_path} is not checked for routers")
                logger.exception(e)

        return routers_data
