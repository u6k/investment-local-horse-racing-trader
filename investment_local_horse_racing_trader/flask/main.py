from flask import Flask, request, g
from selenium.webdriver.common.by import By

from investment_local_horse_racing_trader.app_logging import get_logger
from investment_local_horse_racing_trader.scrapy import app_common


logger = get_logger(__name__)


app = Flask(__name__)


@app.route("/api/health")
def health():
    logger.info("#health: start")

    browser = app_common.open_browser()
    try:

        browser.get("https://www.oddspark.com/keiba/")
        browser.find_element(By.CSS_SELECTOR, "body")

        logger.debug(f"#health: title={browser.title}")

        return browser.title

    finally:
        browser.close()
        browser.quit()
