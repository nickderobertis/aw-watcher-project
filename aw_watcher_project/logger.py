import logging
import sys

logger = logging.getLogger("project_watcher")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s: %(message)s")

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
