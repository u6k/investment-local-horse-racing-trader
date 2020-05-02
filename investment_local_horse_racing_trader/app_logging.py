import warnings
import logging
import logging.config


logging.config.dictConfig({
    "version": 1,

    "formatters": {
        "investment_local_horse_racing_trader.logging.format": {
            "format": "%(asctime)s - %(levelname)-5s [%(name)s] %(message)s",
        },
    },

    "handlers": {
        "investment_local_horse_racing_trader.logging.handler": {
            "class": "logging.StreamHandler",
            "formatter": "investment_local_horse_racing_trader.logging.format",
            "level": logging.DEBUG,
        },
    },

    "loggers": {
        "investment_local_horse_racing_trader": {
            "handlers": ["investment_local_horse_racing_trader.logging.handler"],
            "level": logging.DEBUG,
            "propagate": 0,
        },
        "boto3": {
            "level": logging.INFO,
        },
        "botocore": {
            "level": logging.INFO,
        },
    },
})

warnings.simplefilter("ignore")

logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("selenium").setLevel(logging.INFO)


def get_logger(name):
    return logging.getLogger(name)
