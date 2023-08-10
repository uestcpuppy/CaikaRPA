from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import database
import json
from datetime import datetime
import config_request
import urllib.parse
import config_account

class citic(Bank):
  def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    super().__init__(BankName = "CITIC",
                     Browser = "Chrome",
                     LoginUrl = "https://corp.bank.ecitic.com/cotb/login.html",
                     BinPath = "",
                     LoginPasswd = LoginPasswd,
                     ConfirmPasswd = ConfirmPasswd,
                     BeginDate = BeginDate,
                     EndDate = EndDate,
                     BatchId = BatchId,
                     SlotNum = SlotNum,
                     LoginAccount = LoginAccount)

  def login(self):
    self.initWebdriver()
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    self.logger.info("等待广告")
    WebDriverWait(self.Webdriver, 15, 0.2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#advertPop>div.modal-dialog>div>div.modal-header>button')))
    self.logger.info("关闭广告")
    self.Webdriver.execute_script('document.querySelector("div[id=advertPop] button").click()')
    self.logger.info("切换到密码登录TAB页")
    self.Webdriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div/div[1]/span[2]").click()
    self.logger.info("输入账号")
    time.sleep(1)
    self.Webdriver.find_element(By.XPATH, '//*[@id="userNameorphone"]/div/input').send_keys(self.LoginAccount)
    self.logger.info("输入登录密码")
    self.Webdriver.find_element(By.XPATH, '//*[@id="passwordId"]').click()
    time.sleep(1)
    self.sendkeysRemote(self.LoginPasswd)
    time.sleep(1)
    self.logger.info("点击登录按钮")
    self.Webdriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div/div[2]/button").click()
    self.logger.info("等待首页加载完成")
    WebDriverWait(self.Webdriver, 30, 0.2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="popoverOprNm"]')))
    self.logger.info("结束登录")
    return True

  def queryBalance(self):
      current_date = datetime.now().strftime("%Y%m%d")
      data = config_request.citic_request_balance
      data["startDate"] = current_date
      data["endDate"] = current_date
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      self.logger.info("执行js")
      result = self.sendHttpRequest("post", "/cotb/COTBServlet", json.dumps(data))
      if result["ret"] and result["response"]!="":
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          balance = response_data["myBnkAccBalInfList"][0]["avlBal"]
          self.logger.info("查询余额成功:"+balance)
          database.updateExecution(executionId=self.BatchId, balance=balance)
      else:
          self.logger.info("查询余额失败")
          raise Exception("queryBalance failed!")

  def query(self):
      data = config_request.citic_request_detaillist
      data["startDate"] = self.BeginDate.replace("-", "")
      data["endDate"] = self.EndDate.replace("-", "")
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      self.logger.info("执行js")
      result = self.sendHttpRequest("post", "/cotb/COTBServlet",json.dumps(data))
      if result["ret"] and result["response"] != "":
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          filepath = response_data["retExcelFilePath"]
          self.logger.info("获取文件路径成功:" + filepath)
          result_download = self.sendHttpRequest("get", "/cotb/FileOprServlet?type=1&filename="+filepath,"")
          if result_download["ret"] == True and result_download["download"] == "true":
              self.logger.info("发送文件下载请求成功")
              return True
          else:
              self.logger.info("发送文件下载请求失败")
              raise Exception("download file failed!")
      else:
          self.logger.info("获取文件路径失败")
          raise Exception("get filepath failed!")
      return True

  def ack(self):
      self.logger.info("查询数据条数")
      self.logger.info("执行js")
      data = config_request.citic_request_ack_datacount
      data["startDate"] = self.BeginDate.replace("-", "")
      data["endDate"] = self.EndDate.replace("-", "")
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      result = self.sendHttpRequest("post", "/cotb/COTBServlet", json.dumps(data))
      if result["ret"] and result["response"] != "":
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          totalNum = response_data["totalNum"]
          if int(totalNum) == 0:
              raise Exception("totalNum is zero!")
          else:
              self.logger.info("数据条数:"+totalNum)
      else:
          self.logger.info("查询数据条数失败")
          raise Exception("get totalNum failed!")
      self.logger.info("执行js")
      data = config_request.citic_request_ack_download
      data["startDate"] = self.BeginDate.replace("-", "")
      data["endDate"] = self.EndDate.replace("-", "")
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      result = self.sendHttpRequest("post", "/cotb/COTBServlet", json.dumps(data))
      if result["ret"] and result["response"] != "":
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          filepath = response_data["retOtherFilePath"]
          self.logger.info("获取回单文件路径成功:" + filepath)
          result_download = self.sendHttpRequest("get", "/cotb/FileOprServlet?type=1&filename="+filepath,"")
          if result_download["ret"] == True and result_download["download"] == "true":
              self.logger.info("发送回单下载请求成功")
              return True
          else:
              self.logger.info("发送回单下载请求失败")
              raise Exception("download ack file failed!")
      else:
          self.logger.info("获取回单文件路径失败")
          raise Exception("get ack filepath failed!")
      return True
  def download(self):
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
