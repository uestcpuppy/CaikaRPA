from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import uiautomation as auto
from command import retry_on_exception
import ait
import win32gui
from win32.lib import win32con

class ccb(Bank):
  def __init__(self, LoginPasswd, ConfirmPasswd ,BeginDate, EndDate, BatchId, SlotNum, LoginAccount):

    super().__init__(BankName = "CCB",
                     Browser = "Chrome",
                     LoginUrl = "http://www.ccb.com/cn/jump/b2b_login/login_index.html",
                     BinPath = "",
                     LoginPasswd = LoginPasswd,
                     ConfirmPasswd = ConfirmPasswd,
                     BeginDate = BeginDate,
                     EndDate = EndDate,
                     BatchId = BatchId,
                     SlotNum = SlotNum,
                     LoginAccount = LoginAccount)

  @retry_on_exception(max_attempts=3, interval=3)
  #可以重复, 前提是进入了查询页
  def main_query(self):
      self.logger.info("返回上级frame")
      self.Webdriver.switch_to.parent_frame()
      # 修改起止日期
      js = 'document.querySelector("#StDt").value = "' + self.BeginDate.replace("-", "") + '"\n' \
           'document.querySelector("#EdDt").value = "' + self.EndDate.replace("-", "") + '"'
      self.logger.info("修改起止日期:" + js)
      self.Webdriver.execute_script(js)
      time.sleep(2)
      self.logger.info("切换到页面最后")
      self.Webdriver.find_element(By.XPATH, '/html/body/form/div[2]/div/input[1]').send_keys(Keys.END)
      self.logger.info("点击确定")
      time.sleep(2)
      self.Webdriver.find_element(By.XPATH, '/html/body/form/div[2]/div/input[1]').click()
  @retry_on_exception(max_attempts=5, interval=2)
  #可以重复, 前提是进入了账户选择页
  def select_account_and_query(self):
      self.logger.info("点击全选checkbox")
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, "all_0")))
      cb = self.Webdriver.find_element(By.ID, 'all_0')
      cb.click()
      if not cb.is_selected():
          self.logger.info("checkbox未选中")
          raise Exception("checkbox not selected")
      self.logger.info("点击交易明细按钮")
      self.Webdriver.execute_script("detailQuery()")

  @retry_on_exception(max_attempts=3, interval=2)
  #可以重复, 前提是已经进入了首页
  def get_query_page(self):
      self.logger.info("切换到outFrame")
      self.Webdriver.switch_to.default_content()
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'outFrame')))
      self.logger.info("点击建行活期账户")
      self.Webdriver.execute_script("goTx('5111')")
      self.logger.info("切换frame win_5111")
      self.Webdriver.switch_to.frame("win_5111")
      self.logger.info("切换frame accIframe")
      self.Webdriver.switch_to.frame("accIframe")

  @retry_on_exception(max_attempts=3)
  #可以重复, 但应该是关闭浏览器之后重新打开才彻底
  def get_login_page(self):
      self.initWebdriver()
      self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
      self.Webdriver.get(self.LoginUrl)
      self.logger.info("等待jumpBtn加载完成")
      button = auto.ButtonControl(AutomationId="jumpBtn")
      if button.Exists(maxSearchSeconds=10):
          self.logger.info("页面加载完成,点击登录按钮")
          button.Click()
          time.sleep(2)
          self.logger.info("确认使用证书")
          # 如何判断证书确认页存在 ?
          self.pressEnterRemote()
          self.logger.info("查找U盾密码输入框")
          win = auto.PaneControl(Depth=1, Name='中国建设银行网银盾', searchInterval=0.2, ClassName="#32770")
          if win.Exists(maxSearchSeconds=10):
              self.logger.info("找到U盾密码框")
          else:
              self.logger.info("找不到U盾密框")
              raise Exception("ukey password pane not found!")
      else:
          self.logger.info("登录页加载失败")
          raise Exception("login page load failed")

  @retry_on_exception(max_attempts=2)
  #可以重复, 没有问题
  def input_ukey_passwd(self):
      focused_control = auto.GetFocusedControl().NativeWindowHandle
      nTextLen = win32gui.SendMessage(focused_control, win32con.WM_GETTEXTLENGTH, 0, 0)
      #清空密码
      if nTextLen > 0:
          for i in range(10):
              ait.press('Backspace')
      self.logger.info("输入U盾密码")
      time.sleep(1)
      self.sendkeysRemote(self.ConfirmPasswd)
      #对比已输入密码和应输入密码长度是否一致
      time.sleep(1)
      nTextLen = win32gui.SendMessage(focused_control, win32con.WM_GETTEXTLENGTH, 0, 0)
      if nTextLen != len(self.ConfirmPasswd):
          self.logger.info("U盾密码长度错误")
          raise Exception("ukey password lenght not match")
      self.logger.info("回车")
      self.pressEnterRemote()
      self.logger.info("等待页面加载完成")
      time.sleep(2)
      win = auto.PaneControl(Depth=1, Name='中国建设银行网银盾', searchInterval=0.2, ClassName="#32770")
      if win.Exists(maxSearchSeconds=3):
          self.logger.info("还需要再次输入U盾密码")
          raise Exception("need input password again")
      self.logger.info("登录页加载完成")

  @retry_on_exception(max_attempts=3)
  #可以重复没有问题, 前提是登录页已经加载成功了
  def input_login_passwd(self):
      self.logger.info("开始登录页处理")
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.url_to_be("https://b2b.ccb.com/NCCB/V6/b2bmain.jsp"))
      self.Webdriver.switch_to.default_content()
      self.logger.info("切换到outFrame")
      fr = self.Webdriver.find_element(By.NAME, 'outFrame')
      self.Webdriver.switch_to.frame(fr)
      self.logger.info("切换到fclogin")
      fr2 = self.Webdriver.find_element(By.ID, 'fclogin')
      self.Webdriver.switch_to.frame(fr2)
      self.logger.info("等待LOG_PWD密码框加载完成")
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, 'LOG_PWD')))
      self.logger.info("点击并清空密码框")
      self.Webdriver.find_element(By.ID, 'LOG_PWD').clear()
      self.Webdriver.find_element(By.ID, 'LOG_PWD').click()
      time.sleep(1)
      self.sendkeysRemote(self.LoginPasswd)
      #检查密码长度是否相符
      passwd = self.Webdriver.find_element(By.ID, 'LOG_PWD').get_attribute("value")
      if len(passwd) != len(self.LoginPasswd):
          raise Exception("login passwd length wrong!")
      time.sleep(1)
      self.pressEnterRemote()
      self.logger.info("结束登录")

  @retry_on_exception(ignore_exception=True)
  #可以重复, 前提是当前有2个窗口, 即便出错, 也不会抛出异常
  def close_ad(self):
      self.logger.info("关闭广告")
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.number_of_windows_to_be(2))
      hwd = self.Webdriver.window_handles
      self.Webdriver.switch_to.window(hwd[1])
      self.Webdriver.close()
      self.Webdriver.switch_to.window(hwd[0])
      self.logger.info("关闭广告成功")

  @retry_on_exception(max_attempts=3)
  def download_file(self):
      self.logger.info("点击下载全部")
      WebDriverWait(self.Webdriver, 15, 0.2).until(EC.element_to_be_clickable((By.ID, "dlAll")))
      self.logger.info("下载Excel")
      self.Webdriver.execute_script("submitSelect('1', '2', 'selectDownLoadDiv')")

  def login(self):
    self.get_login_page()
    self.input_ukey_passwd()
    self.close_ad()
    self.input_login_passwd()
    return True

  def query(self):
    self.close_ad()
    self.get_query_page()
    self.select_account_and_query()
    self.main_query()
    return True

  def download(self):
      self.logger.info("开始下载")
      self.download_file()
      self.download_file_chrome()
      self.logger.info("结束下载")
      return True