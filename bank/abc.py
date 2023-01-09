from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uiautomation

class abc(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "ABC"
    self.BinPath = ""
    self.LoginUrl = "https://corporbank.abchina.com/CorporServPlat/netBank/zh_CN/CorporServPlatStartUpAct.do"
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
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    #点击密码控件
    uiautomation.EditControl(AutomationId='1000').Click()
    time.sleep(0.5)
    self.logger.info("输入登录密码")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(0.5)
    self.logger.info("点击登录按钮")
    self.Webdriver.execute_script('document.getElementById("m-kbbtn").click()')
    #等待加载首页
    WebDriverWait(self.Webdriver, 15, 0.2).until(
        EC.url_to_be("https://cbank.abchina.com.cn/CorporServPlat/startUpHtmlSessionAction.do"))
    self.logger.info("结束登录")
    return True

  def query(self):
    # self.Webdriver.switch_to.parent_frame()
    self.logger.info("开始查询")
    #等待一级菜单加载完成
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#oneNav > a:nth-child(2)")))
    self.logger.info("点击账户")
    self.Webdriver.execute_script('document.querySelector("#oneNav > a:nth-child(2)").click()')
    # 等待二级菜单加载完成
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#twoNav > li:nth-child(2)")))
    self.logger.info("点击账户明细查询")
    self.Webdriver.execute_script('document.querySelector("#twoNav > li:nth-child(2)").click()')
    #等待contentFrame加载完成并切换
    self.logger.info("切换到contentFrame")
    self.logger.info("切换frame 1")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "contentFrame")))
    self.logger.info("切换frame 2")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "contentFrame")))

    self.logger.info("点击下载Excel Radio")
    self.Webdriver.execute_script('document.querySelector("#excelRadioOnline").click()')
    #修改起止日期
    js = 'document.getElementById("calendar1").value = "'+self.BeginDate+'"\n' \
         'document.getElementById("calendar2").value = "'+self.EndDate+'"'
    self.logger.info("修改起止日期:"+js)
    self.Webdriver.execute_script(js)
    self.logger.info("完成查询")
    return True

  def download(self):
      self.logger.info("点击下载明细按钮")
      self.Webdriver.execute_script('javascript:submitform6("3950")')
      # time.sleep(3)
      self.logger.info("点击菜单扩展按钮")
      saveAs = uiautomation.SplitButtonControl(Name="6", Depth=5)
      if not saveAs.Exists(6, 0.2):
          self.logger.info("无可下载的数据")
          self.saveScreenShot()
          return True
      saveAs.Click()
      self.logger.info("点击另存为按钮")
      saveAsButton = uiautomation.MenuItemControl(AutomationId="53409", searchInterval=0.5)
      saveAsButton.Click()
      self.logger.info("修改保存路径")
      dirEC = uiautomation.EditControl(AutomationId='1001')
      filePath = self.DownloadTempPath+self.BankName+"_"+self.BatchId + ".xlsx"
      dirEC.SendKeys(filePath)
      self.logger.info("点击保存")
      uiautomation.ButtonControl(AutomationId='1').Click()
      time.sleep(5)
      self.logger.info("从临时文件夹move到正式文件夹")
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
      self.login()
      self.query()
      self.download()
      self.quit()