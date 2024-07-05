import sys
from loguru import logger
import settings
import re


class Formatter:
    """
    Formatter to remove sensitive data such as password, apiKeys and etc
    from: https://github.com/Delgan/loguru/issues/17#issuecomment-717318455
    """
    def __init__(self, scrub_patterns=None):
        super().__init__()
        self.scrub_patterns = scrub_patterns
        self.fmt = settings.LOGURU_FORMAT

    def format(self, record):
        for search, replace in self.scrub_patterns.items():
            record["message"] = re.sub(search, replace, record["message"])
        return settings.LOGURU_FORMAT


# Regexes to remove sensitive data
scrub_patterns = {
    r'\'(authorization|password|cookie)\': \'(.*?)\'': r"'\1': '[REDACTED]'",
    r'"(access_token|refresh_token|)":"(.*?)"': r"'\1':'[REDACTED]'",
}

formatter = Formatter(scrub_patterns=scrub_patterns)

logger.remove()
logger.add(
    sys.stderr,
    format=formatter.format,
    level=settings.LOG_LEVEL,
    backtrace=settings.LOGURU_BACKTRACE,
    diagnose=settings.LOGURU_DIAGNOSE,
)
