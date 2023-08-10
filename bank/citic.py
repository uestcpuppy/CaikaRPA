from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import uiautomation as auto

class citic(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd,BeginDate, EndDate, BatchId, SlotNum):
    self.BankName = "CITIC"
    self.BinPath = ""
    self.LoginUrl = "https://corp.bank.ecitic.com/cotb/login.html"
    self.LoginPasswd = LoginPasswd
    self.ConfirmPasswd = ConfirmPasswd
    # 可能有多个银行账号
    self.Accounts = ""
    self.DownloadPath = "D:\\bankmgr"
    self.BeginDate = BeginDate
    self.EndDate = EndDate
    self.Logger = ""
    self.Browser = "Chrome"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.Webdriver.minimize_window()
    # #等待5秒, 关闭自动弹出的IE浏览器
    time.sleep(10)
    self.killIeRemote()

    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()

    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[id=advertPop] button')))
    #关闭广告
    self.Webdriver.execute_script('document.querySelector("div[id=advertPop] button").click()')
    self.logger.info("关闭广告")

    self.logger.info("等待U盾加载完成")
    #判断U盾是否加载完成
    WebDriverWait(self.Webdriver, 10, 0.2).until(
      EC.text_to_be_present_in_element_value((By.XPATH, '//*[@id="certList"]'), "("))
    #点击密码控件
    self.logger.info("点击密码控件")
    ele = self.Webdriver.find_element(By.ID, 'passwordId')
    self.highlight(ele)
    ele.click()

    #输入密码
    self.logger.info("输入登录密码")
    time.sleep(1)
    self.sendkeysRemote(self.LoginPasswd)
    # self.pressAit(self.LoginPasswd)

    # 首次登录需再次输入U盾密码
    self.Webdriver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div/div/div[2]/button').click()
    time.sleep(3)
    self.logger.info("需输入U盾密码")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(2)
    self.pressEnterRemote()

    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.url_to_be("https://corp.bank.ecitic.com/cotb/index_new.html"))
    self.logger.info("结束登录")

    return True

  def query(self):
    self.logger.info("开始查询")
    menu = self.Webdriver.find_element(By.ID, '00102011')
    self.highlight(menu)
    #time.sleep(2)
    self.logger.info("点击明细查询菜单")
    menu.click()
    #等待查询页加载完成
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="m00102011"]/div[2]/div/div[3]/form/ul/li[1]/div/div[3]/label')))
    #self.logger.info("点击查询本月Radio")
    #self.Webdriver.find_element(By.XPATH, '//*[@id="m00102011"]/div[2]/div/div[3]/form/ul/li[1]/div/div[3]/label').click()
    js = 'document.getElementsByName("startDate")[0].value ="' + self.BeginDate + '" \n'
    js = js + 'document.getElementsByName("endDate")[0].value ="' + self.EndDate + '"'
    self.logger.info("执行js:"+js)
    self.Webdriver.execute_script(js)
    self.logger.info("点击查询按钮")
    self.Webdriver.find_element(By.XPATH, '//*[@id="m00102011"]/div[2]/div/div[7]/div/div/div/ul/li[1]/button').click()
    self.logger.info("结束查询")
    return True

  def download(self):
      self.logger.info("开始下载")
      self.logger.info("点击下载按钮")
      self.Webdriver.find_element(By.XPATH, '//*[@id="droparea-download-all-toggle"]').click()
      self.Webdriver.find_element(By.XPATH, '//*[@id="droparea-download-exc-download"]').click()
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
      self.Webdriver.close()
      return True
