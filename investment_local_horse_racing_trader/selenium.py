import math
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import html
import requests
from uuid import uuid4
from datetime import datetime
from operator import itemgetter


from investment_local_horse_racing_trader.app_logging import get_logger
from investment_local_horse_racing_trader import flask


logger = get_logger(__name__)


def open_browser():
    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")

    browser = webdriver.Remote(
        command_executor="http://selenium-hub:4444/wd/hub",
        desired_capabilities=DesiredCapabilities.CHROME,
        options=options,
    )
    browser.implicitly_wait(10)

    return browser


def login_oddspark(browser):
    user_id = os.getenv("ODDSPARK_USER_ID")
    password = os.getenv("ODDSPARK_PASSWORD")
    pin = os.getenv("ODDSPARK_PIN")

    browser.get("https://www.oddspark.com/keiba/")
    browser.find_element(By.CSS_SELECTOR, "body")
    browser.find_element(By.NAME, "SSO_ACCOUNTID").click()
    browser.find_element(By.NAME, "SSO_ACCOUNTID").send_keys(user_id)
    browser.find_element(By.NAME, "SSO_PASSWORD").click()
    browser.find_element(By.NAME, "SSO_PASSWORD").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "form > a").click()

    browser.find_element(By.NAME, "INPUT_PIN").click()
    browser.find_element(By.NAME, "INPUT_PIN").send_keys(pin)
    browser.find_element(By.NAME, "送信").click()

    browser.find_element(By.CSS_SELECTOR, ".modalCloseImg").click()


def is_logined_oddspark(browser):
    browser.get("https://www.oddspark.com/user/my/Index.do")
    browser.find_element(By.CSS_SELECTOR, "body")

    title = browser.title

    if title.startswith("ログイン"):
        return False
    else:
        return True


def vote(race_id):
    logger.info(f"#vote: start: race_id={race_id}")

    browser = open_browser()
    try:

        # ログイン
        if not is_logined_oddspark(browser):
            login_oddspark(browser)

        # 投票ページを開く
        vote_id = ""  # TODO
        open_vote_page(browser, vote_id)
        # open_vote_page_dummy(browser, vote_id)

        # 投票ページ内容をスクレイピングする
        vote_page_info = scrape_vote_page_info(browser.page_source)
        # vote_page_info = scrape_vote_page_info_dummy(browser.page_source)
        logger.info(f"#vote: vote_page_info={vote_page_info}")

        # 予測順位を取得する
        pred_result = predict_result(race_id, vote_page_info["denma_list"])
        logger.info(f"#vote: pred result={pred_result}")

        # 投資パラメータを取得し、投資サイズを決定する
        target_denma = vote_page_info["denma_list"][pred_result[0] - 1]
        logger.info(f"#vote: target denma={target_denma}")

        if target_denma["odds_win"] is None:
            raise RuntimeError("odds_win is None")

        invest_parameter = get_invest_parameter()
        logger.info(f"#vote: invest_parameter={invest_parameter}")

        vote_cost = calc_vote_cost(vote_page_info["asset"], target_denma["odds_win"], invest_parameter)
        logger.info(f"#vote: asset={vote_page_info['asset']}, vote_cost={vote_cost}")

        # 投票する
        if vote_cost > 0:
            execute_vote(browser, pred_result[0], vote_cost)
            logger.info("#vote: voted")
        else:
            logger.warning("vote abstain: cost == 0")

        # 投票データを記録する
        vote_result = {
            "race_id": race_id,
            "vote_id": vote_id,
            "vote_page_info": vote_page_info,
            "invest_parameter": invest_parameter,
            "vote_horse_number": pred_result[0],
            "vote_cost": vote_cost
        }

        store_vote_data(vote_result)

        return vote_result

    finally:
        browser.close()
        browser.quit()


def open_vote_page(browser, vote_id):
    logger.debug(f"#open_vote_page: start: vote_id={vote_id}")

    browser.get(f"https://www.oddspark.com/keiba/auth/VoteKeibaTop.do?{vote_id}")
    browser.find_element(By.CSS_SELECTOR, "body")

    logger.debug(f"#open_vote_page: title={browser.title}")
    if not browser.title.startswith("投票"):
        logger.warning(f"#open_vote_page: Service is not available")
        raise RuntimeError("Service is not available")


def open_vote_page_dummy(browser, vote_id):
    pass


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


def scrape_vote_page_info_dummy(vote_page_html):
    with open("vote_page.html") as f:
        return scrape_vote_page_info(f.read())


def predict_result(race_id, denma_list):
    logger.debug(f"#predict_result: start: race_id={race_id}")

    # TODO
    resp = requests.get("http://ipinfo.io")

    if resp.status_code != 200:
        raise RuntimeError("Predict API fail")

    sorted_denma_list = sorted(denma_list, key=itemgetter("favorite"))
    pred_result = [d["horse_number"] for d in sorted_denma_list]
    logger.debug(f"#predict_result: pred_result={pred_result}")

    return pred_result


def get_invest_parameter():
    logger.debug(f"#get_invest_parameter: start")

    # TODO
    resp = requests.get("http://ipinfo.io")

    if resp.status_code != 200:
        raise RuntimeError("Get invest_params API fail")

    p = {"algorithm": "dummy", "parameter": {}}
    p["parameter"]["hit_rate"] = 0.1677
    p["parameter"]["kelly_coefficient"] = 0.1524

    return p


def calc_vote_cost(asset, odds, invest_parameter):
    logger.debug(f"#calc_vote_cost: start: asset={asset}, odds={odds}, invest_parameter={invest_parameter}")

    hit_rate = invest_parameter["parameter"]["hit_rate"]
    kelly_coefficient = invest_parameter["parameter"]["kelly_coefficient"]

    if odds > 1.0:
        kelly = (hit_rate * odds - 1.0) / (odds - 1.0)
    else:
        kelly = 0.0
    logger.debug(f"#calc_vote_cost: kelly={kelly}")

    if kelly > 0.0:
        vote_cost = math.floor(asset * kelly * kelly_coefficient / 100.0) * 100
    else:
        vote_cost = 0
    logger.debug(f"#calc_vote_cost: vote_cost={vote_cost}")

    return vote_cost


def execute_vote(browser, horse_number, vote_cost):
    logger.info(f"#execute_vote: horse_number={horse_number}, vote_cost={vote_cost}")

    browser.find_element(By.CSS_SELECTOR, f".n{horse_number}").click()
    browser.find_element(By.ID, "textfield11").click()
    browser.find_element(By.ID, "textfield11").clear()
    browser.find_element(By.ID, "textfield11").send_keys(vote_cost / 100)
    browser.find_element(By.ID, "set").click()

    browser.save_screenshot("vote.png")


def store_vote_data(vote_result):
    logger.info("#store_vote_data: start")

    db_conn = flask.get_db()
    try:
        db_cursor = db_conn.cursor()
        try:

            create_timestamp = datetime.now()

            db_cursor.execute("delete from race_denma where race_id=%s", (vote_result["race_id"],))

            for denma in vote_result["vote_page_info"]["denma_list"]:
                race_denma_id = f"{vote_result['race_id']}_{denma['horse_number']}"

                db_cursor.execute("insert into race_denma (race_denma_id, race_id, vote_id, horse_number, horse_name, favorite, odds_win, create_timestamp) values (%s, %s, %s, %s, %s, %s, %s, %s)", (race_denma_id, vote_result["race_id"], vote_result["vote_id"], denma["horse_number"], denma["horse_name"], denma["favorite"], denma["odds_win"], create_timestamp))

            vote_record_id = str(uuid4())
            bet_type = "win"

            db_cursor.execute("insert into vote_record(vote_record_id, race_id, vote_id, bet_type, horse_number_1, vote_cost, algorithm, vote_parameter, create_timestamp) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (vote_record_id, vote_result["race_id"], vote_result["vote_id"], bet_type, vote_result["vote_horse_number"], vote_result["vote_cost"], vote_result["invest_parameter"]["algorithm"], vote_result["invest_parameter"]["parameter"].__str__(), create_timestamp))

            db_conn.commit()

        finally:
            db_cursor.close()

    finally:
        db_conn.close()
