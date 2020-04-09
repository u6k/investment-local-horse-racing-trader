from selenium.webdriver.common.by import By
from lxml import html

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

        logger.info(f"title={browser.title}")
        if not browser.title.startswith("投票"):
            logger.warning("Service is not available")
            raise RuntimeError("Sercice is not available")

        vote_doc = html.fromstring(browser.page_source)

        vote_page_info = {}

        vote_page_info["asset"] = vote_doc.xpath("//span[@id='buylimit']")[0].text
        logger.info(f"asset={vote_page_info['asset']}")
        vote_page_info["vote_page_info['vote_limit']"] = vote_doc.xpath("//span[@id='betCountlimit']")[0].text
        logger.info(f"vote_limit={vote_page_info['vote_limit']}")

        vote_page_info["denma_list"] = []
        for table in vote_doc.xpath("//table"):
            try:
                if table.attrib["summary"] != "出走表":
                    continue
            except KeyError:
                continue

            for tr in table.xpath(".//tr"):
                if len(tr.xpath("th")) > 0:
                    continue

                if len(tr.xpath("td")) == 8:
                    td_offset = 1
                else:
                    td_offset = 0

                denma = {}
                denma["horse_number"] = tr.xpath("td")[td_offset].text
                denma["horse_name"] = tr.xpath("td")[td_offset+1].text
                denma["favorite_order"] = tr.xpath("td")[td_offset+5].text

                try:
                    int(denma["favorite_order"])
                    denma["odds_win"] = tr.xpath("td")[td_offset+6].xpath("span")[0].text
                except ValueError:
                    denma["odds_win"] = None

                logger.info(f"denma={denma}")

                vote_page_info["denma_list"].append(denma)

        browser.save_screenshot("vote.png")

        return vote_page_info

    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    race_id = "raceDy=yyyymmdd&opTrackCd=xx&sponsorCd=xx&raceNb=x"
    vote_id = "kaisaiBi=yyyymmdd&joCode=xx&raceNo=x"

    vote(race_id, vote_id)
    # health()
