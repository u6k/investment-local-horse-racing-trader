import os
from flask import Flask, request, g
import psycopg2
from psycopg2.extras import DictCursor

from investment_local_horse_racing_trader.app_logging import get_logger
from investment_local_horse_racing_trader import VERSION, selenium


logger = get_logger(__name__)


app = Flask(__name__)


@app.route("/api/health")
def health():
    logger.info("#health: start")

    result = {"version": VERSION}

    # Check oddspark
    logger.debug("#health: check oddspark")

    browser = selenium.open_browser()
    try:

        selenium.login_oddspark(browser)

        is_logined_oddspark = selenium.is_logined_oddspark(browser)
        logger.debug(f"#health: is_logined_oddspark={is_logined_oddspark}")

        result["oddspark"] = is_logined_oddspark

    finally:
        browser.close()
        browser.quit()

    # Check database
    logger.debug("#health: check database")

    db_cursor = get_db().cursor()
    try:

        db_cursor.execute("select 1")
        result["database"] = True

    finally:
        db_cursor.close()

    return result


@app.route("/api/vote", methods=["POST"])
def vote():
    logger.info("#vote: start")

    args = request.get_json()
    logger.debug(f"#vote: args={args}")

    race_id = args.get("race_id", None)

    selenium.vote(race_id)

    return "ok"


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
        g.db.autocommit = False
        g.db.set_client_encoding("utf-8")
        g.db.cursor_factory = DictCursor

    return g.db


@app.teardown_appcontext
def _teardown_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()
