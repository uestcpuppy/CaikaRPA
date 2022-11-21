from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import uiautomation as auto


class cib(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "CIB"
    self.BinPath = ""
    self.LoginUrl = "https://corporatebank.cib.com.cn/firm/main/login.do"
    self.LoginPasswd = LoginPasswd
    self.ConfirmPasswd = ConfirmPasswd
    # 可能有多个银行账号
    self.Account = LoginAccount
    self.DownloadPath = ""
    self.BeginDate = BeginDate
    self.EndDate = EndDate
    self.SlotNum = 0
    self.Logger = ""
    self.Browser = "Ie"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    time.sleep(3)
    self.logger.info("输入U盾密码并回车")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    time.sleep(3)
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.ID,"loginName")))
    time.sleep(1)
    self.logger.info("输入登录账户名")
    # self.sendkeysRemote(self.Account)
    self.pressAit(self.Account)
    time.sleep(1)
    self.logger.info("点击登录密码输入框")
    self.Webdriver.execute_script('document.querySelector("#password").focus()')
    time.sleep(1)
    self.logger.info("输入登录密码并回车")
    # self.sendkeysRemote(self.LoginPasswd)
    self.pressAit(self.LoginPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    self.logger.info("等待首页加载完毕")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://corporatebank.cib.com.cn/firm/main/mainx"))
    self.logger.info("结束登录")
    return True

  def query(self):
    self.logger.info("开始查询")
    self.logger.info("关闭广告")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.visibility_of_element_located((By.ID, "adaptiveAlert-bulletin")))
    self.Webdriver.execute_script('removeAdaptiveDialog("bulletin")')
    self.logger.info("点击交易明细查询菜单")
    self.Webdriver.execute_script('document.getElementById("130100").click()')
    time.sleep(3)
    self.logger.info("切换到workframe")
    WebDriverWait(self.Webdriver, 3, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "workframe")))
    self.logger.info("修改查询起止日期")
    js = 'document.getElementById("startDate").value = "'+self.BeginDate+'"\n' \
         'document.getElementById("endDate").value = "'+self.EndDate+'"'
    self.Webdriver.execute_script(js)
    time.sleep(2)
    self.logger.info("点击查询按钮")
    self.Webdriver.execute_script('document.getElementById("queryOpeBtn").click()')
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.ID, "download")))
    self.Webdriver.find_element(By.ID, 'download').send_keys(Keys.END)
    self.saveScreenShot()
    self.logger.info("结束查询")
    return True
  def download(self):
      self.logger.info("开始下载")
      self.logger.info("点击下载按钮")
      self.Webdriver.execute_script('document.getElementById("download").click()')
      time.sleep(2)
      self.logger.info("返回上级frame")
      self.Webdriver.switch_to.parent_frame()
      try:
          self.logger.info("切换到dialogFrame")
          WebDriverWait(self.Webdriver, 3, 0.2).until(
              EC.frame_to_be_available_and_switch_to_it((By.NAME, "dialogFrame")))
      except Exception as e:
          self.logger.info("切换到dialogFrame失败, 查询数据为空, 结束下载")
          return True
      time.sleep(2)
      self.logger.info("点击下载图标")
      self.Webdriver.execute_script('document.querySelector("div.box img").click()')
      time.sleep(2)
      self.logger.info("发送Ctrl+S保存文件")
      self.pressAltS()
      time.sleep(3)
      downloadFile = self.processDownloadFile()
      if downloadFile == "":
          self.logger.info("下载失败")
      else:
          self.logger.info("下载成功:"+downloadFile)
      self.logger.info("结束下载")
      return True
  def quit(self):
      self.Webdriver.quit()
      return True
  def run(self):
      self.login()
      self.query()
      self.download()
      time.sleep(2)
      self.quit()