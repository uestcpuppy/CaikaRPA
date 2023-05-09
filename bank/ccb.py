import uiautomation
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import ait
import uiautomation as auto


class ccb(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "CCB"
    self.BinPath = ""
    self.LoginUrl = "http://www.ccb.com/cn/jump/b2b_login/login_index.html"
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
    # self.Webdriver.maximize_window()
    self.logger.info("等待jumpBtn加载完成")
    # WebDriverWait(self.Webdriver, 10, 0.2).until(
    #     EC.element_to_be_clickable((By.ID, 'jumpBtn')))
    self.logger.info("点击开始登录按钮")
    # time.sleep(3)
    # self.Webdriver.find_element(By.ID, 'jumpBtn').click()
    time.sleep(5)
    uiautomation.ButtonControl(AutomationId="jumpBtn").Click()
    # time.sleep(5)
    self.pressEnterRemote()
    time.sleep(3)
    self.logger.info("输入U盾密码并回车")
    self.sendkeysRemote(self.ConfirmPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    self.logger.info("等待页面加载完成")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.number_of_windows_to_be(2))
    self.logger.info("登录页加载完成")
    self.logger.info("关闭广告")
    hwd = self.Webdriver.window_handles
    try:
        self.Webdriver.switch_to.window(hwd[1])
        self.Webdriver.close()
    except Exception as e:
        self.logger.info("关闭广告出错")
    self.Webdriver.switch_to.window(hwd[0])
    self.logger.info("切换到outFrame")
    fr = self.Webdriver.find_element(By.NAME, 'outFrame')
    self.Webdriver.switch_to.frame(fr)
    fr2 = self.Webdriver.find_element(By.ID, 'fclogin')
    self.Webdriver.switch_to.frame(fr2)
    self.logger.info("等待LOG_PWD密码框加载完成")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.element_to_be_clickable((By.ID, 'LOG_PWD')))
    self.logger.info("点击密码框")
    # self.Webdriver.execute_script('document.querySelector("#LOG_PWD").focus()')
    # time.sleep(1)
    self.Webdriver.find_element(By.ID, 'LOG_PWD').click()
    time.sleep(1)
    self.sendkeysRemote(self.LoginPasswd)
    time.sleep(2)
    self.pressEnterRemote()
    self.logger.info("结束登录")
    return True


  def query(self):
    self.logger.info("开始查询")
    WebDriverWait(self.Webdriver, 15, 0.2).until(EC.number_of_windows_to_be(2))
    self.logger.info("关闭广告")
    hwd = self.Webdriver.window_handles
    try:
        self.Webdriver.switch_to.window(hwd[1])
        self.Webdriver.close()
    except Exception as e:
        self.logger.info("关闭广告出错")
    self.Webdriver.switch_to.window(hwd[0])
    self.logger.info("切换到outFrame")
    WebDriverWait(self.Webdriver, 10, 0.2).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, 'outFrame')))
    # self.Webdriver.switch_to.frame(self.Webdriver.find_element(By.NAME, 'outFrame'))
    self.logger.info("点击建行活期账户")
    self.Webdriver.execute_script("goTx('5111')")
    self.logger.info("切换frame win_5111")
    # self.waitSwitchFrame(self.Webdriver, By.ID, "win_5111", 5)
    self.Webdriver.switch_to.frame("win_5111")
    self.logger.info("切换frame accIframe")
    # self.waitSwitchFrame(self.Webdriver, By.ID, "accIframe", 5)
    self.Webdriver.switch_to.frame("accIframe")
    self.logger.info("点击全选checkbox")
    WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, "all_0")))
    self.Webdriver.find_element(By.ID, 'all_0').click()
    cb = self.Webdriver.find_element(By.ID, 'all_0')
    if not cb.is_selected():
      self.logger.info("再次点击checkbox")
      time.sleep(2)
      cb.click()

    self.logger.info("点击交易明细按钮")
    self.Webdriver.execute_script("detailQuery()")
    self.logger.info("返回上级frame")

    try:
        self.Webdriver.switch_to.parent_frame()
    except Exception as e:
        self.logger.info("返回上级frame出错")
        time.sleep(3)
        self.Webdriver.switch_to.parent_frame()

    # time.sleep(2)
    # self.waitElementLoad(self.Webdriver, By.ID, "StDt", 5)
    #修改起止日期
    js = 'document.querySelector("#StDt").value = "'+self.BeginDate.replace("-","")+'"\n' \
         'document.querySelector("#EdDt").value = "'+self.EndDate.replace("-","")+'"'
    self.logger.info("修改起止日期:"+js)
    try:
        self.Webdriver.execute_script(js)
    except Exception as e:
        self.logger.info("执行js出错")
        time.sleep(3)
        self.Webdriver.switch_to.parent_frame()
        self.Webdriver.execute_script(js)
    time.sleep(2)
    self.logger.info("切换到页面最后")
    self.Webdriver.find_element(By.XPATH, '/html/body/form/div[2]/div/input[1]').send_keys(Keys.END)
    self.logger.info("点击确定")
    time.sleep(2)
    self.Webdriver.find_element(By.XPATH, '/html/body/form/div[2]/div/input[1]').click()
    self.logger.info("结束查询")
    return True
  def download(self):
      self.logger.info("开始下载")
      self.logger.info("点击下载全部")
      # self.waitElementLoad(self.Webdriver, By.ID, "dlAll", 5)
      WebDriverWait(self.Webdriver, 15, 0.2).until(EC.element_to_be_clickable((By.ID, "dlAll")))
      # self.Webdriver.find_element(By.ID, 'dlAll').click()
      # time.sleep(2)
      self.logger.info("下载Excel")
      self.Webdriver.execute_script("submitSelect('1', '2', 'selectDownLoadDiv')")
      # self.Webdriver.find_element(By.XPATH, '/html/body/div[5]/ul/li[2]').click()
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
  # def run(self):
  #     self.login()
  #     self.query()
  #     self.download()
  #     self.quit()