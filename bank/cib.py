from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import threading
import config
import database

def worker(pwd, obj):
    # time.sleep(5)
    # dd = DDLib()
    # dd.send_keys(pwd)
    # time.sleep(1)
    # dd.dd_dll.DD_key(815, 1)
    # dd.dd_dll.DD_key(815, 2)
    time.sleep(5)
    obj.sendkeysRemote(pwd)
    time.sleep(1)
    obj.pressEnterRemote()


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
    self.Browser = "IeInEdge"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.logger.info("启动异步线程确认证书,输入密码,按回车")
    t = threading.Thread(target=worker, args=(self.ConfirmPasswd,self), daemon=True)
    t.start()
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    # time.sleep(3)
    # self.logger.info("输入U盾密码并回车")
    # self.sendkeysRemote(self.ConfirmPasswd)
    # time.sleep(2)
    # self.pressEnterRemote()
    time.sleep(3)
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.ID,"loginName")))
    time.sleep(1)
    self.logger.info("输入登录账户名")
    # self.sendkeysRemote(self.Account)
    # self.pressAit(self.Account)
    self.Webdriver.find_element(By.ID, 'loginName').send_keys(self.Account)
    time.sleep(1)
    self.logger.info("点击登录密码输入框")
    self.Webdriver.execute_script('document.querySelector("#password").focus()')
    time.sleep(1)
    self.logger.info("输入登录密码")
    self.pressAit(self.LoginPasswd)
    time.sleep(1)
    self.logger.info("勾选隐私条款")
    self.Webdriver.find_element(By.ID, 'privacy_check').click()
    time.sleep(1)
    self.logger.info("确认回车")
    self.pressEnterRemote()
    self.logger.info("等待首页加载完毕")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://corporatebank.cib.com.cn/firm/main/mainx"))
    self.logger.info("结束登录")
    return True

  def query(self):
    self.logger.info("开始查询")
    self.logger.info("关闭广告")

    try:
        self.Webdriver.implicitly_wait(2)
        WebDriverWait(self.Webdriver, 3, 0.2).until(
            EC.visibility_of_element_located((By.ID, "adaptiveAlert-bulletin")))
        self.Webdriver.execute_script('removeAdaptiveDialog("bulletin")')
    except Exception as e:
        self.logger.info("未出现广告页")
    finally:
        self.Webdriver.implicitly_wait(config.IMPLICITLY_WAIT)

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
    self.logger.info("结束查询")
    return True
  def download(self):
      time.sleep(3)
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
          self.saveScreenShot()
          return True
      # time.sleep(300)
      self.logger.info("点击下载图标")
      self.Webdriver.execute_script('document.querySelector("div.box img").click()')
      time.sleep(2)
      if self.downloadFileFromIE():
          self.logger.info("下载成功")
      else:
          self.logger.info("下载失败")
          self.saveScreenShot()
      return True

  def queryBalance(self):
      self.logger.info("开始查询")
      self.logger.info("点击活期账户查询页面")
      self.Webdriver.execute_script('document.getElementById("130010").click()')
      retrytimes = 5
      accountNumStr = ""
      balanceStr = ""
      while retrytimes>0:
        try:
            self.logger.info("切换到workframe")
            self.Webdriver.implicitly_wait(2)
            self.Webdriver.switch_to.frame("workframe")
            # WebDriverWait(self.Webdriver, 10, 0.2).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "workframe")))
            accountNumStr = self.Webdriver.find_element(By.CSS_SELECTOR, 'td[aria-describedby="list_acctNo"]').text
            tempStr = self.Webdriver.find_element(By.CSS_SELECTOR, 'td[aria-describedby="list_availableBalance"]').text
            balanceStr = tempStr.replace(",","").strip()
            self.logger.info("切换到workframe成功")
            break
        except Exception as e:
            self.logger.info("切换到workframe失败")
            retrytimes = retrytimes - 1

      if accountNumStr.find(self.AccountNum) != -1:
          self.logger.info("查询余额成功:" + balanceStr)
          database.updateExecution(executionId=self.BatchId, balance=balanceStr)
      else:
          self.logger.info("查询余额失败: 未找到对应账户数据")
      return True

  def quit(self):
      self.logger.info("退出浏览器开始")
      self.Webdriver.close()
      self.logger.info("退出浏览器成功")
      return True