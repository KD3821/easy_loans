# Thus file includes functions to run some scripts.
# By using them it is possible to separate types of functions
# To use the the file needs to be addes as scripts/run_seeds.py

from .loggers import logger
from .internals import OrmInternalService


def import_from(module_name, name):
    module = __import__(module_name, fromlist=[name])
    return getattr(module, name)


def script_decorate(func):
    def func_wrapper(*args, **kwargs):
        try:
            script_name = args[1]
        except IndexError:
            script_name = "all"

        logger.info(f"Started ***{script_name}*** operation")
        func(*args, **kwargs)
        logger.info(f"finished ***{script_name}*** operation")

    return func_wrapper


@script_decorate
def perform_scripts(scripts_names, scripts_path, name, perform_func_name, args):
    for name in scripts_names:
        perform_script(scripts_path, name, perform_func_name, args[1:])


@script_decorate
def perform_script(scripts_path, scripts_name, perform_func_name, args):
    module_path = f"{scripts_path}.{scripts_name}"
    perform_func = import_from(module_path, perform_func_name)
    perform_func(args)


def perform(args, scripts_path, scripts_names, perform_func_name, is_all_supported):
    # To read all models, thus they
    # will be present in Base.metadata

    OrmInternalService.get_models()
    name = args[1]

    if is_all_supported and name == "all":
        return perform_scripts(scripts_names, scripts_path, name, perform_func_name, args)

    if name in scripts_names:
        return perform_script(scripts_path, name, perform_func_name, args[1:])

    logger.info("***{}*** operation not found", name)
