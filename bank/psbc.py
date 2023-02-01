import uiautomation
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import ait

import uiautomation as auto

class psbc(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "PSBC"
    self.BinPath = ""
    self.LoginUrl = "https://www.psbc.com/cn/"
    self.LoginPasswd = LoginPasswd
    self.ConfirmPasswd = ConfirmPasswd
    # 可能有多个银行账号
    self.Account = LoginAccount
    self.DownloadPath = ""
    self.BeginDate = BeginDate
    self.EndDate = EndDate
    self.SlotNum = 0
    self.Logger = ""
    self.Browser = "Chrome"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    self.logger.info("等待企业网银按钮加载完成")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/a[2]')))
    self.logger.info("点击开始登录按钮")
    ait.move(344,319)
    ait.click()
    time.sleep(2)
    self.logger.info("输入U盾密码并回车")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    self.logger.info("等待页面加载完成")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://corpebank.psbc.com/#/login"))
    self.Webdriver.find_element(By.ID,'ukeyLogin').click()
    self.sendkeysRemote(self.LoginPasswd)
    self.Webdriver.find_element(By.XPATH, '//*[@id="pane-ukeyLogin"]/form/button').click()
    self.logger.info("结束登录")
    return True


  def query(self):
    self.logger.info("开始查询")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://corpebank.psbc.com/#/index"))
    self.logger.info("点击交易明细")
    time.sleep(2)
    self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[1]/form/button[1]').click()
    self.logger.info("点击查询")
    time.sleep(2)
    self.Webdriver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/form/div/div[3]/div/div/div/label[5]').click()
    time.sleep(1)
    self.Webdriver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[2]/button[2]').click()
    time.sleep(2)
    self.logger.info("结束查询")
    return True
  def download(self):
      self.logger.info("开始下载")
      self.logger.info("点击下载")
      self.Webdriver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[1]/div[2]/div[2]/span').click()
      time.sleep(0.5)
      self.logger.info("点击excel")
      self.Webdriver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[1]/div[2]/div[2]/ol/li[2]').click()
      time.sleep(0.5)
      self.logger.info("点击按照日期升序")
      self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[5]/div/div[2]/span/button[1]').click()
      time.sleep(5)
      downloadFile = self.processDownloadFile()
      if downloadFile == "":
          self.logger.info("下载失败")
          self.saveScreenShot()
      else:
          self.logger.info("下载成功:"+downloadFile)
      self.logger.info("结束下载")
      return True
  def quit(self):
      self.Webdriver.quit()
      return True
  def run(self):
      # time.sleep(5)
      self.login()
      self.query()
      self.download()
      time.sleep(3)
      self.quit()