from selenium.webdriver.common.by import By

import app_common


logger = app_common.get_logger()


def health():
    browser = app_common.open_browser()
    try:

        browser.get("https://www.oddspark.com/keiba/")
        browser.find_element(By.CSS_SELECTOR, "body")

        logger.info(browser.title)
        browser.save_screenshot("health.png")

    finally:
        browser.close()
        browser.quit()


def vote(race_id, vote_id):
    browser = app_common.open_browser()
    try:

        if not app_common.is_logined_oddspark(browser):
            app_common.login_oddspark(browser)

        browser.get(f"https://www.oddspark.com/keiba/auth/VoteKeibaTop.do?{vote_id}")
        browser.find_element(By.CSS_SELECTOR, "body")

        logger.info(browser.title)
        browser.save_screenshot("vote.png")

    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    race_id = "raceDy=20200409&opTrackCd=43&sponsorCd=33&raceNb=12"
    vote_id = "kaisaiBi=20200409&joCode=43&raceNo=8"

    vote(race_id, vote_id)
    # health()
