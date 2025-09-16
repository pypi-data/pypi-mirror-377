# -*- coding: utf-8 -*-
import logging
from .. import env
import sys
log_level = env.LOG_LEVEL

logger = logging.getLogger("app")
logger.setLevel(log_level)
# console_handler = logging.StreamHandler(stream=sys.stdout)
# console_handler.setLevel(log_level)
# logger.addHandler(console_handler)
