from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

class spdb(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd,  BeginDate, EndDate, BatchId, SlotNum):
    self.BankName = "SPDB"
    self.BinPath = ""
    self.LoginUrl = "https://ebanksent.spdb.com.cn/newent/gb/login/prof.jsp"
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
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    self.Webdriver.find_element(By.XPATH, '//*[@id="modal-confirm"]').click()
    self.logger.info("确认U盾是否加载完成")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.text_to_be_present_in_element_value((By.ID, "LoginId2"), "002"))
    self.logger.info("点击密码框")
    self.Webdriver.find_element(By.XPATH, '//*[@id="OPassword"]').click()
    time.sleep(2)
    self.logger.info("输入登录密码")
    self.sendkeysRemote(self.LoginPasswd)
    time.sleep(2)
    self.logger.info("点击登录按钮")
    # 首次登录需再次输入U盾密码, 超时即认为首次登录
    try:
        self.Webdriver.execute_script('document.querySelector("#loginSubmit").click()')
    except TimeoutException as e:
        self.logger.info("超时需要输入U盾密码")
        self.sendkeysRemote(self.ConfirmPasswd)
        time.sleep(2)
        self.pressEnterRemote()
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://ebanksent.spdb.com.cn/msent-web-home/main.do"))
    self.logger.info("结束登录")
    return True

  def query(self):
    self.logger.info("开始查询")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="mainpage"]/div[1]/div[3]/div[2]/div/ul[1]/li[2]/div/a')))
    self.logger.info("点击明细查询菜单")
    self.Webdriver.find_element(By.XPATH, '//*[@id="mainpage"]/div[1]/div[3]/div[2]/div/ul[1]/li[2]/div/a').click()
    time.sleep(5)
    self.logger.info("切换到iframe1")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "iframe1")))
    time.sleep(3)
    #修改起止日期
    js = 'document.getElementById("BeginDate1").value = "'+self.BeginDate+'"\n' \
         'document.getElementById("EndDate1").value = "'+self.EndDate+'"'
    self.logger.info("修改起止日期:"+js)
    self.Webdriver.execute_script(js)
    time.sleep(3)
    self.logger.info("移动到页面最后")
    self.Webdriver.find_element(By.CSS_SELECTOR, '#search').send_keys(Keys.END)
    self.logger.info("点击查询")
    time.sleep(2)
    self.Webdriver.find_element(By.CSS_SELECTOR, '#search').click()
    time.sleep(3)
    self.logger.info("结束查询")
    return True
  def download(self):
      self.logger.info("开始下载")
      self.logger.info("移动到页面最后")
      self.Webdriver.implicitly_wait(0)
      try:
        WebDriverWait(self.Webdriver, 3, 0.2).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="EXCELDown"]')))
        self.Webdriver.find_element(By.XPATH, '//*[@id="EXCELDown"]').send_keys(Keys.END)
      except Exception as e:
          self.logger.info("查询数据为空")
          self.saveScreenShot()
          return True
      time.sleep(2)
      self.logger.info("点击EXCEL下载")
      self.Webdriver.find_element(By.XPATH, '//*[@id="EXCELDown"]').click()
      time.sleep(5)
      self.logger.info("切换到新窗口")
      self.Webdriver.switch_to.window(self.Webdriver.window_handles[1])
      time.sleep(2)
      self.logger.info("点击保存")
      self.Webdriver.find_element(By.XPATH, '//*[@id="CompFlagButton"]').click()
      time.sleep(3)
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
      time.sleep(3)
      self.quit()

