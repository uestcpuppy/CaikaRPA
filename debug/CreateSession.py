import sys
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

sys.path.append("..")
# 这里是自己下载的ie驱动
iedriver = Service('D:\\Python37\\Scripts\\IEDriverServer.exe')
driver = webdriver.Ie(service=iedriver)
url = driver.command_executor._url
session_id = driver.session_id
print(driver.session_id)
print(driver.command_executor._url)

config = configparser.ConfigParser()
config.add_section("IE")
config.set("IE", "url", url)
config.set("IE", "session_id", session_id)

with open("session.ini", "w+") as f:
    config.write(f)
f.close()