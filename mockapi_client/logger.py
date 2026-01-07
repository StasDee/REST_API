import logging
import colorlog

def get_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a colorized logger instance that can be used across the project.
    """
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(levelname)s] %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    # Silence noisy third-party logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return logger
