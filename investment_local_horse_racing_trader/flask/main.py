from flask import Flask, request, g

from investment_local_horse_racing_trader.app_logging import get_logger


logger = get_logger(__name__)


app = Flask(__name__)


@app.route("/api/health")
def health():
    logger.info("#health: start")

    return "ok"
