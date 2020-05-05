import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import html
import requests
from requests.auth import HTTPBasicAuth
from uuid import uuid4
from datetime import datetime
import json
import urllib.parse
import time


from investment_local_horse_racing_trader.app_logging import get_logger
from investment_local_horse_racing_trader import flask


logger = get_logger(__name__)


def open_browser():
    logger.info("#open_browser: start")

    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")

    browser = webdriver.Remote(
        command_executor="http://selenium-hub:4444/wd/hub",
        desired_capabilities=DesiredCapabilities.CHROME,
        options=options,
    )
    browser.implicitly_wait(10)

    logger.debug("#open_browser: opened")

    return browser


def login_oddspark(browser):
    logger.info("#login_oddspark: start")

    user_id = os.getenv("ODDSPARK_USER_ID")
    password = os.getenv("ODDSPARK_PASSWORD")
    pin = os.getenv("ODDSPARK_PIN")

    browser.get("https://www.oddspark.com/keiba/")
    browser.find_element(By.CSS_SELECTOR, "body")
    browser.find_element(By.NAME, "SSO_ACCOUNTID").click()
    browser.find_element(By.NAME, "SSO_ACCOUNTID").send_keys(user_id)
    browser.find_element(By.NAME, "SSO_PASSWORD").click()
    browser.find_element(By.NAME, "SSO_PASSWORD").send_keys(password)
    browser_screenshot(browser, "login")
    browser.find_element(By.CSS_SELECTOR, "form > a").click()
    logger.debug("#login_oddspark: input login")

    browser.find_element(By.NAME, "INPUT_PIN").click()
    browser.find_element(By.NAME, "INPUT_PIN").send_keys(pin)
    browser_screenshot(browser, "pin")
    browser.find_element(By.NAME, "送信").click()
    logger.debug("#login_oddspark: input pin")

    browser.find_element(By.CSS_SELECTOR, ".modalCloseImg").click()
    browser_screenshot(browser, "top")
    logger.debug("#login_oddspark: close modal")


def is_logined_oddspark(browser):
    logger.info("#is_logined_oddspark: start")

    browser.get("https://www.oddspark.com/user/my/Index.do")
    browser.find_element(By.CSS_SELECTOR, "body")
    browser_screenshot(browser, "mypage")

    title = browser.title

    if title.startswith("ログイン"):
        result = False
    else:
        result = True

    logger.debug(f"#is_logined_oddspark: result={result}")
    return result


def vote(race_id, vote_cost_limit, dry_run=True):
    logger.info(f"#vote: start: race_id={race_id}, vote_cost_limit={vote_cost_limit}, dry_run={dry_run}")

    # 予測する
    last_asset = get_last_asset()
    predict_result = predict(race_id, last_asset, vote_cost_limit)
    vote_record_id = store_predict_data(predict_result)

    if predict_result["vote_cost"] > 0 and not dry_run:
        browser = open_browser()
        try:
            # ログイン
            if not is_logined_oddspark(browser):
                login_oddspark(browser)

            # 投票ページを開く
            vote_id = build_vote_id(race_id)
            open_vote_page(browser, vote_id)

            # 投票する
            execute_vote(browser, predict_result["horse_number"], predict_result["vote_cost"])
            store_vote_data(vote_record_id, predict_result["vote_cost"])

        finally:
            browser.close()
            browser.quit()
    else:
        logger.debug("#vote: cancel: vote_cost is 0")

    logger.debug(f"#vote: predict_result={predict_result}")
    return predict_result


def vote_close(race_id):
    vote_record = find_vote_record(race_id)

    race_result = find_race_result(race_id, vote_record["horse_number"])

    if race_result["result"] == 1:
        vote_return = vote_record["vote_cost"] * race_result["result_odds"]
    else:
        vote_return = 0

    close_result = {
        "vote_record_id": vote_record["vote_record_id"],
        "result": race_result["result"],
        "result_odds": race_result["result_odds"],
        "vote_return": vote_return,
    }

    store_vote_result(close_result["vote_record_id"], close_result["result"], close_result["result_odds"], close_result["vote_return"])

    return close_result


def open_vote_page(browser, vote_id):
    logger.debug(f"#open_vote_page: start: vote_id={vote_id}")

    browser.get(f"https://www.oddspark.com/keiba/auth/VoteKeibaTop.do?{vote_id}")
    browser.find_element(By.CSS_SELECTOR, "body")
    browser_screenshot(browser, "vote")

    logger.debug(f"#open_vote_page: title={browser.title}")
    if not browser.title.startswith("投票"):
        logger.warning(f"#open_vote_page: Service is not available")
        raise RuntimeError("Service is not available")


def scrape_vote_page_info(vote_page_html):
    logger.debug("#scrape_vote_page_info: start")

    vote_doc = html.fromstring(vote_page_html)

    vote_page_info = {}

    vote_page_info["asset"] = int(vote_doc.xpath("//span[@id='buylimit']")[0].text.replace("円", "").replace(",", ""))
    logger.debug(f"#scrape_vote_page_info: asset={vote_page_info['asset']}")
    vote_page_info["vote_limit"] = int(vote_doc.xpath("//span[@id='betCountlimit']")[0].text)
    logger.debug(f"#scrape_vote_page_info: vote_limit={vote_page_info['vote_limit']}")
    vote_page_info["round"] = int(vote_doc.xpath("//ul[@id='racenum']/li[contains(@class,'active')]/@value")[0])
    logger.debug(f"#scrape_vote_page_info: round={vote_page_info['round']}")

    vote_page_info["denma_list"] = []
    for table in vote_doc.xpath("//table"):
        logger.debug("#scrape_vote_page_info: table found")

        try:
            if table.attrib["summary"] != "出走表":
                continue
        except KeyError:
            continue

        logger.debug("#scrape_vote_page_info: denma table")
        for tr in table.xpath(".//tr"):
            logger.debug("#scrape_vote_page_info: tr")
            if len(tr.xpath("th")) > 0:
                logger.debug("#scrape_vote_page_info: is header")
                continue

            if len(tr.xpath("td")) == 8:
                td_offset = 1
            else:
                td_offset = 0

            denma = {}
            denma["horse_number"] = int(tr.xpath("td")[td_offset].text)
            denma["horse_name"] = tr.xpath("td")[td_offset+1].text
            denma["favorite"] = tr.xpath("td")[td_offset+5].text

            try:
                denma["favorite"] = int(denma["favorite"])
                denma["odds_win"] = float(tr.xpath("td")[td_offset+6].xpath("span")[0].text)
            except ValueError:
                denma["odds_win"] = None

            logger.debug(f"#scrape_vote_page_info: denma={denma}")
            vote_page_info["denma_list"].append(denma)

    return vote_page_info


def predict(race_id, asset, vote_cost_limit):
    logger.info(f"#predict: start: race_id={race_id}, asset={asset}, vote_cost_limit={vote_cost_limit}")

    url = os.getenv("API_PREDICT_URL")
    headers = {
        "Content-Type": "application/json",
    }
    auth = HTTPBasicAuth(os.getenv("API_PREDICT_AUTH_USER"), os.getenv("API_PREDICT_AUTH_PASSWORD"))
    params = json.dumps({
        "race_id": race_id,
        "asset": asset,
        "vote_cost_limit": vote_cost_limit,
    })
    logger.debug(f"#predict: url={url}, params={params}")

    resp = requests.post(url=url, headers=headers, auth=auth, data=params)
    logger.debug(f"#predict: status_code={resp.status_code}, body={resp.text}")

    return resp.json()


def execute_vote(browser, horse_number, vote_cost):
    logger.info(f"#execute_vote: start: horse_number={horse_number}, vote_cost={vote_cost}")

    browser.find_element(By.CSS_SELECTOR, f".n{horse_number}").click()
    browser.find_element(By.ID, "textfield11").click()
    browser.find_element(By.ID, "textfield11").clear()
    browser.find_element(By.ID, "textfield11").send_keys(str(int(vote_cost / 100)))
    browser.find_element(By.ID, "set").click()
    browser_screenshot(browser, "vote_input")
    browser.find_element(By.ID, "gotobuy").click()
    logger.debug("#execute_vote: input vote")

    time.sleep(5)

    browser.find_element(By.CSS_SELECTOR, "body")
    browser_screenshot(browser, "vote_confirm")
    browser.find_element(By.ID, "buy").click()
    logger.debug("#execute_vote: confirm vote")

    time.sleep(5)

    browser.find_element(By.CSS_SELECTOR, "body")
    browser_screenshot(browser, "vote_complete")
    logger.debug("#execute_vote: complete vote")


def store_predict_data(predict_result):
    logger.info(f"#store_predict_data: start: predict_result={predict_result}")

    db_conn = flask.get_db()
    db_cursor = db_conn.cursor()
    try:

        create_timestamp = datetime.now()

        vote_record_id = str(uuid4())
        bet_type = "win"

        db_cursor.execute("insert into vote_record(vote_record_id, race_id, bet_type, horse_number_1, odds, vote_cost, vote_parameter, create_timestamp) values (%s, %s, %s, %s, %s, %s, %s, %s)", (vote_record_id, predict_result["race_id"], bet_type, predict_result["horse_number"], predict_result["odds_win"], 0, predict_result["parameters"].__str__(), create_timestamp))

        db_conn.commit()

        logger.info(f"#store_predict_data: vote_record_id={vote_record_id}")

        return vote_record_id

    finally:
        db_cursor.close()


def store_vote_data(vote_record_id, vote_cost):
    logger.info(f"#store_vote_data: start: vote_record_id={vote_record_id}, vote_cost={vote_cost}")

    db_conn = flask.get_db()
    db_cursor = db_conn.cursor()
    try:

        db_cursor.execute("update vote_record set vote_cost=%s where vote_record_id=%s", (vote_cost, vote_record_id))
        db_conn.commit()

    finally:
        db_cursor.close()


def get_last_asset():
    logger.info("#get_last_asset: start")

    db_cursor = flask.get_db().cursor()
    try:

        db_cursor.execute("select sum(vote_cost) from vote_record")
        (total_vote_cost,) = db_cursor.fetchone()

        db_cursor.execute("select sum(vote_return) from vote_record")
        (total_vote_return,) = db_cursor.fetchone()

        last_asset = total_vote_return - total_vote_cost
        logger.debug(f"#get_last_asset: total_vote_cost={total_vote_cost}, total_vote_return={total_vote_return}, last_asset={last_asset}")

        return last_asset

    finally:
        db_cursor.close()


def find_vote_record(race_id):
    logger.info(f"#find_vote_record: start: race_id={race_id}")

    db_cursor = flask.get_db().cursor()
    try:

        db_cursor.execute("select vote_record_id, race_id, bet_type, horse_number_1, odds, vote_cost from vote_record where race_id = %s", (race_id,))
        (vote_record_id, race_id, bet_type, horse_number_1, odds, vote_cost) = db_cursor.fetchone()

        vote_record = {"vote_record_id": vote_record_id, "race_id": race_id, "bet_type": bet_type, "horse_number": horse_number_1, "odds": odds, "vote_cost": vote_cost}
        logger.debug(f"#find_vote_record: vote_record={vote_record}")

        return vote_record

    finally:
        db_cursor.close()


def find_race_result(race_id, horse_number):
    logger.info(f"#find_race_result: start: race_id={race_id}, horse_number={horse_number}")

    db_cursor = flask.get_crawler_db().cursor()
    try:

        db_cursor.execute("""
            select
                result,
                odds_win
            from
                race_result as r join odds_win as o on
                    r.race_id = o.race_id
                    and r.horse_number = o.horse_number
            where
                r.race_id = %s
                and r.horse_number = %s""", (race_id, horse_number))

        (result, odds_win) = db_cursor.fetchone()

        race_result = {"result": result, "result_odds": odds_win}
        logger.debug(f"#find_race_result: race_result={race_result}")

        return race_result

    finally:
        db_cursor.close()


def store_vote_result(vote_record_id, result, result_odds, vote_return):
    logger.info(f"#store_vote_result: start: vote_record_id={vote_record_id}, result={result}, result_odds={result_odds}, vote_return={vote_return}")

    db_conn = flask.get_db()
    db_cursor = db_conn.cursor()
    try:

        update_timestamp = datetime.now()

        db_cursor.execute("update vote_record set result=%s, result_odds=%s, vote_return=%s, update_timestamp=%s where vote_record_id=%s", (result, result_odds, vote_return, update_timestamp, vote_record_id))

        db_conn.commit()

        logger.info(f"#store_vote_result: updated")

    finally:
        db_cursor.close()


def build_vote_id(race_id):
    logger.info(f"#build_vote_id: start: race_id={race_id}")

    d = urllib.parse.parse_qs(race_id)
    vote_id = f"kaisaiBi={d['raceDy'][0]}&joCode={d['opTrackCd'][0]}&raceNo={d['raceNb'][0]}"
    logger.debug(f"#build_vote_id: vote_id={vote_id}")

    return vote_id


def browser_screenshot(browser, name):
    logger.info(f"#browser_screenshot: start")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/var/screenshot/{timestamp}.{name}.png"

    browser.save_screenshot(filename)
