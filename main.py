from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

browser = webdriver.Remote(
    command_executor="http://selenium-hub:4444/wd/hub",
    desired_capabilities=DesiredCapabilities.CHROME
)

browser.get("https://www.google.co.jp")

sleep(1)

browser.save_screenshot("test.png")

browser.close()
browser.quit()