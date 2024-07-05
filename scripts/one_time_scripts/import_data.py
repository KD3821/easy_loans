from core import logger
import asyncio


def perform(args):
    try:
        setting = {
            'name': args[1],
        }
    except IndexError:
        logger.error("""
            Incorrect arguments for the script
            The format is: ... run_script import_data <name>
            Example: ./manage.sh run_script import_data test
        """)
        return

    logger.info(
        f"\nImporting {setting['name']} data")

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(main(setting))


async def main(setting):
    logger.info(f"Imported {setting['name']} data")
