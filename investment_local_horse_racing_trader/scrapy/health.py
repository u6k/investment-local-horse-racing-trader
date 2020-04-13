from selenium.webdriver.common.by import By

from investment_local_horse_racing_trader.scrapy import app_common


logger = app_common.get_logger()


def health():
    logger.info("#health: start")

    browser = app_common.open_browser()
    try:

        browser.get("https://www.oddspark.com/keiba/")
        browser.find_element(By.CSS_SELECTOR, "body")

        logger.info(f"#health: title={browser.title}")

        return browser.title

    finally:
        browser.close()
        browser.quit()
