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
    self.Browser = "IE"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    #点击密码控件
    uiautomation.EditControl(AutomationId='1000').Click()
    time.sleep(3)
    self.logger.info("输入登录密码")
    self.sendkeysRemote(self.LoginPasswd)
    time.sleep(2)
    self.logger.info("点击登录按钮")
    self.Webdriver.set_script_timeout(15)
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
    self.logger.info("begin")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "contentFrame")))
    self.logger.info("end")
    time.sleep(3)
    # print (self.Webdriver.current_window_handle.)
    #农行有2种不同的查询界面, 完全不同
    #第一种查询界面的处理
    # WebDriverWait(self.Webdriver, 20, 0.2).until(
    #     EC.element_to_be_clickable((By.ID, "excelRadioOnline")))
    self.logger.info("点击下载Excel Radio")
    self.Webdriver.execute_script('document.querySelector("#excelRadioOnline").click()')
    # self.Webdriver.find_element(By.ID, 'excelRadioOnline')
    # self.Webdriver.find_element(By.ID, 'excelRadioOnline').send_keys(Keys.SPACE)
    #等待时间控件加载完成
    self.logger.info("begin1")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.visibility_of_element_located((By.ID, "calendar1")))
    self.logger.info("end1")
    #修改起止日期
    js = 'document.getElementById("calendar1").value = "'+self.BeginDate+'"\n' \
         'document.getElementById("calendar2").value = "'+self.EndDate+'"'
    self.logger.info("修改起止日期:"+js)
    self.Webdriver.execute_script(js)
    self.logger.info("完成查询")
    return True
    #以下为第二种查询界面
    # WebDriverWait(self.Webdriver, 10, 0.2).until(
    #     EC.presence_of_element_located((By.XPATH, '//div[@id="pane-first"]')))
    # self.logger.info("修改开始结束日期")
    # js = 'contentFrame.document.querySelector("input[placeholder=\\"开始日期\\"]").value ="' + self.BeginDate + '" \n'
    # js = js + 'contentFrame.document.querySelector("input[placeholder=\\"结束日期\\"]").value ="' + self.EndDate + '"'
    # self.logger.info("执行js:"+js)
    # self.Webdriver.execute_script(js)
    # time.sleep(3)
    # time.sleep(3)
    # self.Webdriver.execute_script('contentFrame.document.querySelector(\'input[class="el-range-input"]\').click()')
    # time.sleep(3)
    # self.Webdriver.execute_script('contentFrame.document.querySelector("button[class=\'el-picker-panel__shortcut\']:nth-child(3)").click()')
  def download(self):
      self.logger.info("点击下载明细按钮")
      self.Webdriver.execute_script('javascript:submitform6("3950")')
      time.sleep(3)
      self.logger.info("发送Ctrl+S保存文件")
      self.pressAltS()
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
      # self.Webdriver.close()
      return True
  def run(self):
      self.login()
      self.query()
      self.download()
      time.sleep(3)
      self.quit()