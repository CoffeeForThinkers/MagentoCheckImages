import logging

_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def configure(is_debugging):
    logger = logging.getLogger()

    if is_debugging is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    formatter = logging.Formatter(_LOG_FORMAT)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
