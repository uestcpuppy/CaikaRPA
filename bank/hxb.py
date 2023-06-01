from bank.bank import Bank
import uiautomation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import threading
from DD.DDLib import DDLib
import database

def worker(pwd):
    time.sleep(5)
    dd = DDLib()
    dd.send_keys(pwd)
    time.sleep(1)
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)

class hxb(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "HXB"
    self.BinPath = ""
    self.LoginUrl = "https://dbank.hxb.com.cn/gluebanking/login.html?k=true"
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
    t = threading.Thread(target=worker, args=(self.ConfirmPasswd,), daemon=True)
    t.start()
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    # self.logger.info("等待jumpBtn加载完成")
    # WebDriverWait(self.Webdriver, 10, 0.2).until(
    #     EC.element_to_be_clickable((By.ID, 'jumpBtn')))
    # self.logger.info("点击开始登录按钮")
    # # time.sleep(3)
    # # self.Webdriver.find_element(By.ID, 'jumpBtn').click()
    # uiautomation.ButtonControl(AutomationId="jumpBtn").Click()
    # time.sleep(1)
    # self.pressEnterRemote()
    # time.sleep(300)
    # self.logger.info("输入U盾密码并回车")
    # self.sendkeysRemote(self.ConfirmPasswd)
    # time.sleep(2)
    # self.pressEnterRemote()
    self.logger.info("按tab键盘切换到密码输入框")
    self.Webdriver.find_element(By.ID, "login_submit").send_keys(Keys.SHIFT, Keys.TAB)
    self.logger.info("输入登陆密码")
    self.sendkeysRemote(self.LoginPasswd)
    time.sleep(1)
    self.logger.info("点击登陆按钮")
    self.Webdriver.find_element(By.ID, "login_submit").click()
    WebDriverWait(self.Webdriver, 15, 0.2).until(EC.url_contains("https://dbank.hxb.com.cn/gluebanking/welcomemanage/welcomeset/welcomePage_show.html"))
    self.logger.info("结束登录")
    return True


  def query(self):
    self.logger.info("开始查询")
    self.Webdriver.find_element(By.XPATH, '//*[@id="cygnul"]/LI[3]/A').click()

    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.ID, 'strdate')))

    #修改起止日期
    js = 'document.querySelector("#strdate").value = "'+self.BeginDate+'"\n' \
         'document.querySelector("#enddate").value = "'+self.EndDate+'"'
    self.logger.info("修改起止日期:"+js)
    self.Webdriver.execute_script(js)
    time.sleep(2)
    self.Webdriver.execute_script("listAcctOrder()")
    time.sleep(2)
    self.logger.info("结束查询")
    return True

  def download(self):
      self.logger.info("开始下载")
      self.logger.info("判断是否查询结果为空")
      if self.Webdriver.find_element(By.ID, 'crMoney').text == "":
          self.logger.info("无可下载的数据")
          self.saveScreenShot()
          return True
      self.logger.info("下载全部Excel")
      self.Webdriver.execute_script("downFile(0,1)")
      time.sleep(2)
      if self.downloadFileFromIE():
          self.logger.info("下载成功")
      else:
          self.logger.info("下载失败")
          self.saveScreenShot()

  def quit(self):
      self.Webdriver.quit()
      return True

  def queryBalance(self):
      self.logger.info("开始查询余额")
      self.logger.info("点击账户管理菜单")
      self.Webdriver.find_element(By.XPATH, '/HTML/BODY/DIV[3]/DIV/UL/LI[2]/A').click()
      accountStr = self.Webdriver.find_element(By.XPATH,'/HTML/BODY/DIV[4]/DIV[2]/TABLE[1]/TBODY/TR[2]/TD[3]').text
      balanceStr = self.Webdriver.find_element(By.XPATH,'/HTML/BODY/DIV[4]/DIV[2]/TABLE[1]/TBODY/TR[2]/TD[6]').text
      balanceStr = balanceStr.replace(",", "").strip()
      if accountStr.find(self.AccountNum) != -1:
          self.logger.info("查询余额成功:" + balanceStr)
          database.updateExecution(executionId=self.BatchId, balance=balanceStr)
      else:
          self.logger.info("查询余额失败: 未找到对应账户数据")
      time.sleep(3)
      return True