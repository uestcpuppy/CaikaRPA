from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import database
import uiautomation as auto
from command import retry_on_exception
import ait
import win32gui
from win32.lib import win32con
import config_account
from lxml import html
import urllib.parse
import config_request

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


  @retry_on_exception(max_attempts=3)
  #可以重复, 但应该是关闭浏览器之后重新打开才彻底
  def get_login_page(self):
      self.initWebdriver()
      self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
      self.Webdriver.get(self.LoginUrl)
      self.logger.info("等待jumpBtn加载完成")
      #button = auto.ButtonControl(AutomationId="jumpBtn")
      fr2 = self.Webdriver.find_element(By.ID, 'fclogin')
      self.Webdriver.switch_to.frame(fr2)
      time.sleep(5)
      WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, 'jumpBtn')))
      self.logger.info("点击开始登录按钮")
      self.Webdriver.find_element(By.ID, 'jumpBtn').click()

      if True:
          self.logger.info("页面加载完成,点击登录按钮")
          # button.click()
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

  def login(self):
    self.get_login_page()
    self.input_ukey_passwd()
    self.close_ad()
    self.input_login_passwd()
    self.close_ad()
    WebDriverWait(self.Webdriver, 10, 0.2).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'outFrame')))
    skey = self.Webdriver.find_element(By.ID, "SKEY").get_attribute('value')
    self.skey = skey
    self.logger.info("SKEY is:"+skey)
    return True

  def query(self):
    data = config_request.ccb_request_datalist_getfile
    data["SKEY"] = self.skey
    data["StDt"] = self.BeginDate.replace("-", "")
    data["EdDt"] = self.EndDate.replace("-", "")
    #账户相关参数
    data["USERID"] = config_account.config[self.AccountNum]["USERID"]
    data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
    data["checkedAccnoInfor"] = config_account.config[self.AccountNum]["checkedAccnoInfor"]
    data["checkedAccName"] = config_account.config[self.AccountNum]["checkedAccName"]
    data["checkedAccno"] = config_account.config[self.AccountNum]["checkedAccno"]
    data["ACC_NO"] = config_account.config[self.AccountNum]["ACC_NO_3"]

    query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    self.logger.info("执行js")
    result = self.sendHttpRequest("post", "/NCCB/NECV6B2BMainPlat_02", query_str)
    if result["ret"] and result["response"] != "":
        self.logger.info("获取文件页面成功")
        self.logger.info(result["response"])
        res = result["response"]
        pos_start = res.find("jhform.FILEPATH.value")
        pos_end = res.find(";", pos_start)
        filepath = res[pos_start+24:pos_end-1]
        tree = html.fromstring(res)
        inputs = tree.xpath('/html/body/form/input[2]')
        filename = inputs[0].value
        data = config_request.ccb_request_datalist_download
        data["SKEY"] = self.skey
        data["FILEPATH"] = filepath
        data["FILENAME"] = filename
        data["SOURCE"] = filename
        # 账户相关参数
        data["USERID"] = config_account.config[self.AccountNum]["USERID"]
        data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
        query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
        result_download = self.sendHttpRequest("post", "/NCCB/NECV6FileDownload_02", query_str)
        if result_download["ret"] == True and result_download["download"] == "true":
            self.logger.info("发送文件下载请求成功")
            return True
        else:
            self.logger.info("发送文件下载请求失败")
            raise Exception("download file failed!")
    else:
        self.logger.info("获取文件页面失败")
        raise Exception("get file download page failed!")
    return True

  def queryBalance(self):
      data = config_request.ccb_request_balance
      data["SKEY"] = self.skey
      # 账户相关参数
      data["USERID"] = config_account.config[self.AccountNum]["USERID"]
      data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
      data["ACCT_NO"] = config_account.config[self.AccountNum]["ACCT_NO_2"]

      query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
      self.logger.info("执行js")
      result = self.sendHttpRequest("get", '/NCCB/NECV6B2BMainPlat_02?'+query_str, "")
      if result["ret"] and result["response"]!="":
          res = result['response'].strip()
          pos_start = 0
          pos_end = res.find("::")
          balance = res[pos_start:pos_end]
          if balance.find(".") != -1:
            self.logger.info("查询余额成功:"+balance)
            database.updateExecution(executionId=self.BatchId, balance=balance)
            return True
      self.logger.info("查询余额失败")
      raise Exception("queryBalance failed!")

  def ack(self):
      data = config_request.ccb_request_ack_apply
      data["SKEY"] = self.skey
      data["BEGIN_DATE"] = self.BeginDate.replace("-", "")
      data["END_DATE"] = self.EndDate.replace("-", "")
      # 账户相关参数
      data["USERID"] = config_account.config[self.AccountNum]["USERID"]
      data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
      data["ACCT_NO"] = config_account.config[self.AccountNum]["ACCT_NO_1"]
      query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
      self.logger.info("提交下载回单请求")
      #其中的FILEPATH是什么？ 为什么的固定的？
      result = self.sendHttpRequest("post", "/NCCB/NECV6B2BMainPlat_02",query_str)
      if result["ret"] and result["response"] != "":
          res = result["response"]
          tree = html.fromstring(res)
          inputs = tree.xpath('/html/body/form/input[6]')
          taskId = inputs[0].value
          self.logger.info("批次号:"+taskId)
          #根据回单号, 查询下载任务状态
          retryTime = 10
          while retryTime > 0:
              self.logger.info("获得回单异步下载列表")
              data = config_request.ccb_request_ack_tasklist
              data["SKEY"] = self.skey
              # 账户相关参数
              data["USERID"] = config_account.config[self.AccountNum]["USERID"]
              data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
              data["ACCT_NO"] = config_account.config[self.AccountNum]["ACCT_NO_1"]
              data["Cst_AccNo"] = config_account.config[self.AccountNum]["Cst_AccNo"]
              query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
              result = self.sendHttpRequest("post", "/NCCB/NECV6B2BMainPlat_02",query_str)
              try:
                  if result["ret"] and result["response"] != "":
                      self.logger.info(result["response"])
                      res = result["response"]
                      pos_start = res.find(taskId) + 35
                      pos_end = pos_start + 60
                      tempTaskStatus = res[pos_start:pos_end].strip()
                      if tempTaskStatus.find("download") != -1:
                          self.logger.info("任务状态为已完成:"+taskId)
                          break
                      else:
                          self.logger.info("任务状态为:" + tempTaskStatus)
                          time.sleep(10)
                          pass

              except Exception as e:
                  self.logger.info("获得回单异步下载列表失败")
                  raise

          data = config_request.ccb_request_ack_getfile
          data["SKEY"] = self.skey
          data["MnTsk_ID"] = taskId
          # 账户相关参数
          data["USERID"] = config_account.config[self.AccountNum]["USERID"]
          data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
          data["Cst_AccNo"] = config_account.config[self.AccountNum]["Cst_AccNo"]
          query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
          result = self.sendHttpRequest("post", "/NCCB/NECV6B2BMainPlat_02",query_str)

          res = result["response"].strip()
          self.logger.info(res)
          mid_pos = res.find("　")
          filepath = res[3:mid_pos]
          filename = res[mid_pos + 1:]

          data = config_request.ccb_request_ack_download
          data["SKEY"] = self.skey
          data["FILEPATH"] = filepath
          data["FILENAME"] = filename
          data["SOURCE"] = filename
          # 账户相关参数
          data["USERID"] = config_account.config[self.AccountNum]["USERID"]
          data["CUSTOMERID"] = config_account.config[self.AccountNum]["CUSTOMERID"]
          data["Cst_AccNo"] = config_account.config[self.AccountNum]["Cst_AccNo"]
          query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)

          result_download = self.sendHttpRequest("post", "/NCCB/NECV6FileDownload_02", query_str)
          if result_download["ret"] == True and result_download["download"] == "true":
              self.logger.info("发送文件下载请求成功")
              return True
          else:
              self.logger.info("发送文件下载请求失败")
              raise Exception("download file failed!")
      else:
          self.logger.info("申请异步下载失败")
          raise Exception("apply ack file failed!")
      return True

  def download(self):
      self.logger.info("开始下载")
      self.download_file_chrome()
      self.logger.info("结束下载")
      return True