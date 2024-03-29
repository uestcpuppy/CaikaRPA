import database
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class icbc(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "ICBC"
    self.BinPath = ""
    self.LoginUrl = "https://corporbank-simp.icbc.com.cn/icbc/normalbank/index.jsp"
    self.LoginPasswd = LoginPasswd
    self.ConfirmPasswd = ConfirmPasswd
    # 可能有多个银行账号
    self.Accounts = ""
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

    time.sleep(3)
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)

    #切换frame
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "indexFrame")))
    time.sleep(2)
    self.logger.info("点击U盾登录按钮")
    self.Webdriver.find_element(By.ID, 'usubmitkey').click()
    time.sleep(2)
    self.pressEnterRemote()
    time.sleep(4)
    # if self.Webdriver.current_url == "https://corporbank-simp.icbc.com.cn/ebankc/normalbank/guide.jsp":
    #     self.logger.info("没有检测到U盾")
    #     raise Exception("no usbkey detected")
    self.logger.info("输入密码并按回车")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    time.sleep(1)
    self.logger.info("结束登录")
    # time.sleep(1000)
    return True

  def query(self):
    self.logger.info("开始查询")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "mainFrame")))
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="acctRightBlock"]/div/div[3]/a[1]')))
    self.logger.info("点击首页的明细查询")
    self.Webdriver.find_element(By.XPATH, '//*[@id="acctRightBlock"]/div/div[3]/a[1]').click()
    #下载按钮
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div/form[13]/div[11]/button[4]')))
    self.logger.info("修改起止日期")

    js = 'datepicker1.setInitBeginDate("'+self.BeginDate.replace("-","")+'")\n' \
         'datepicker1.setInitEndDate("'+self.EndDate.replace("-","")+'")\n' \
         'datepicker1.show()'

    self.logger.info("修改隐藏的起止日期:"+js)
    self.Webdriver.execute_script(js)
    time.sleep(3)
    self.logger.info("结束查询")
    return True
  def download(self):
      self.logger.info("开始下载")
      self.logger.info("点击下载按钮")
      self.Webdriver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/form[13]/div[11]/button[4]').click()
      time.sleep(3)
      downloadFrame = self.Webdriver.find_element(By.XPATH,'//*[@id="ebdp-pc4ebankc-floatdialog-window-downLoadJump"]/div[2]/iframe')
      self.Webdriver.switch_to.frame(downloadFrame)
      time.sleep(1)
      self.Webdriver.find_element(By.XPATH, '/html/body/div[1]/p/button[2]').click()
      time.sleep(3)
      downloadFile = self.processDownloadFile()
      if downloadFile == "":
          self.logger.info("下载失败")
          self.saveScreenShot()
      else:
          self.logger.info("下载成功:"+downloadFile)
      self.logger.info("结束下载")
      return True

  def queryBalance(self):
      # document.querySelector("").innerText
      self.logger.info("查询账户余额")
      WebDriverWait(self.Webdriver, 10, 0.2).until(
          EC.frame_to_be_available_and_switch_to_it((By.NAME, "mainFrame")))
      self.Webdriver.find_element(By.ID, 'searchBtn').click()
      tempStr = self.Webdriver.find_element(By.CSS_SELECTOR, '#balancediv > span.ebankc-mcp-marginright20').text
      if tempStr.find("人民币") == -1:
          self.logger.info("查询余额失败")
      else:
          self.logger.info("查询余额成功:" + tempStr[4:-1].replace(",",""))
          database.updateExecution(executionId=self.BatchId, balance=tempStr[4:-1].replace(",",""))
      time.sleep(3)
      return True

  def quit(self):
      self.Webdriver.close()
      return True