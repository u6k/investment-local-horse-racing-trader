import os
from flask import Flask, request, g
import psycopg2
from psycopg2.extras import DictCursor
from queue import Queue
import time
import functools

from investment_local_horse_racing_trader.app_logging import get_logger
from investment_local_horse_racing_trader import VERSION, selenium


logger = get_logger(__name__)


app = Flask(__name__)


singleQueue = Queue(maxsize=1)


def multiple_control(q):
    def _multiple_control(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            q.put(time.time())
            logger.debug("#multiple_control: start: critical zone")
            result = func(*args, **kwargs)
            logger.debug("#multiple_control: end: critical zone")
            q.get()
            q.task_done()
            return result
        return wrapper
    return _multiple_control


@app.route("/api/health")
def health():
    logger.info("#health: start")

    try:
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

    except Exception:
        logger.exception("error")
        return "error", 500


@app.route("/api/vote", methods=["POST"])
@multiple_control(singleQueue)
def vote():
    logger.info("#vote: start")

    try:
        args = request.get_json()
        logger.debug(f"#vote: args={args}")

        race_id = args.get("race_id", None)
        dry_run = args.get("dry_run", True)

        vote_result = selenium.vote(race_id, dry_run)

        return vote_result

    except Exception:
        logger.exception("error")
        return "error", 500


@app.route("/api/vote_close", methods=["POST"])
@multiple_control(singleQueue)
def vote_close():
    logger.info("#vote_close: start")

    try:
        args = request.get_json()
        logger.debug(f"#vote_close: args={args}")

        race_id = args.get("race_id", None)

        close_result = selenium.vote_close(race_id)

        return close_result

    except Exception:
        logger.exception("error")
        return "error", 500


@app.route("/api/deposit", methods=["POST"])
def deposit():
    logger.info("#deposit: start")

    try:
        args = request.get_json()
        logger.debug(f"#deposit: args={args}")

        deposit_asset = args.get("asset")

        predict_result = {
            "race_id": "deposit",
            "horse_number": 0,
            "odds_win": 0,
            "vote_cost": 0,
            "parameters": "deposit"
        }
        vote_record_id = selenium.store_vote_data(predict_result)

        selenium.store_vote_result(vote_record_id, 0, 0, deposit_asset)

        last_asset = selenium.get_last_asset()

        return {"last_asset": last_asset}

    except Exception:
        logger.exception("error")
        return "error", 500


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


def get_crawler_db():
    if "crawler_db" not in g:
        g.crawler_db = psycopg2.connect(
            host=os.getenv("CRAWLER_DB_HOST"),
            port=os.getenv("CRAWLER_DB_PORT"),
            dbname=os.getenv("CRAWLER_DB_DATABASE"),
            user=os.getenv("CRAWLER_DB_USERNAME"),
            password=os.getenv("CRAWLER_DB_PASSWORD")
        )
        g.crawler_db.autocommit = False
        g.crawler_db.set_client_encoding("utf-8")
        g.crawler_db.cursor_factory = DictCursor

    return g.crawler_db


@app.teardown_appcontext
def _teardown_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

    crawler_db = g.pop("crawler_db", None)
    if crawler_db is not None:
        crawler_db.close()
