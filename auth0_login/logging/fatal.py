import logging


def fatal(msg, *args, **kwargs):
    """
    log fatal `msg` and exit
    """
    logging.error(msg, *args, **kwargs)
    exit(1)