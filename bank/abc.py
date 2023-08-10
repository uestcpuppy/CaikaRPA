import config
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import database
import config_account
import config_request

class abc(Bank):
  def __init__(self,  LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
    self.BankName = "ABC"
    self.BinPath = ""
    self.LoginUrl = "https://ebank.abchina.com.cn/CorporServCloud/cfsp-static/#/logonUpdating"
    self.LoginPasswd = LoginPasswd
    self.ConfirmPasswd = ConfirmPasswd
    # 可能有多个银行账号
    self.Account = LoginAccount
    self.DownloadPath = ""
    self.BeginDate = BeginDate
    self.EndDate = EndDate
    self.Logger = ""
    self.Browser = "IeInEdge"
    self.BatchId = BatchId
    self.SlotNum = SlotNum
    super().__init__()

  def login(self):
    self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
    self.Webdriver.get(self.LoginUrl)
    self.Webdriver.maximize_window()
    self.logger.info("点击登录按钮")
    try:
        self.Webdriver.set_page_load_timeout(5)
        self.Webdriver.find_element(By.ID, "m-kbbtn").click()
    except Exception as e:
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.ConfirmPasswd)
        time.sleep(1)
        self.logger.info("按回车")
        self.pressEnterRemote()
    finally:
        self.Webdriver.set_page_load_timeout(20)
    self.logger.info("等待加载首页")
    WebDriverWait(self.Webdriver, 15, 0.2).until(EC.url_to_be("https://cbank.abchina.com.cn/CorporServPlat/startUpHtmlSessionAction.do"))
    self.logger.info("结束登录")
    return True

  def download(self):
      if self.downloadFileFromIE():
          self.logger.info("下载成功")
      else:
          self.logger.info("下载失败")
          self.saveScreenShot()
      return True

  def queryBalance(self):
      self.logger.info("等待一级菜单加载完成")
      WebDriverWait(self.Webdriver, 20, 0.2).until(
          EC.visibility_of_element_located((By.CSS_SELECTOR, "#oneNav > a:nth-child(2)")))
      time.sleep(5)
      self.logger.info("执行js")
      data = config_request.abc_request_balance
      data["fromAccNme"] = config_account.config[self.AccountNum]["fromAccNme"]
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      #result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/acc/v1/balanceMore",'{"qryList":[{"fromAccNme":"北京糖豆儿娱乐文化传媒有限公司","currency":"156","accNo":"11-230501040008301","fromCryTypNme":"人民币","fromAccCha":"601","fromAccChaNme":"支票户","fromAccNetId":"112305","fromCahrmFlg":"0"}]}')
      result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/acc/v1/balanceMore",json.dumps(data))

      if result["ret"] and result["response"]!="":
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          balance = response_data["data"]["countList"]["人民币"]["aAccBal"]
          self.logger.info("查询余额成功:"+balance)
          database.updateExecution(executionId=self.BatchId, balance=balance)
      else:
          self.logger.info("查询余额失败")
          raise Exception("queryBalance failed!")
      return True

  def query(self):
      self.logger.info("等待一级菜单加载完成")
      WebDriverWait(self.Webdriver, 20, 0.2).until(
          EC.visibility_of_element_located((By.CSS_SELECTOR, "#oneNav > a:nth-child(2)")))
      time.sleep(5)
      self.logger.info("执行js")
      #data = '{"dowmloadType":"1","ordDrec":"1","maxReqNum":"10","fromCstAcc":"11-230501040008301","fromCryTyp":"156","fromAccNme":"北京糖豆儿娱乐文化传媒有限公司","fromCryTypNme":"人民币","fromAccCha":"601","fromAccChaNme":"支票户","fromCahrmFlg":"0","fromAccNetId":"112305","sDte":"%s","eDte":"%s","detailList":[]}'%(self.BeginDate.replace("-", ""), self.EndDate.replace("-", ""))
      data = config_request.abc_request_detaillist
      data["fromCstAcc"] = config_account.config[self.AccountNum]["fromCstAcc"]
      data["fromAccNme"] = config_account.config[self.AccountNum]["fromAccNme"]
      data["sDte"] = self.BeginDate.replace("-", "")
      data["eDte"] = self.EndDate.replace("-", "")
      result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/detail/v1/downloadAcctDetailNew", json.dumps(data))
      if result["ret"] and result["download"] == "true":
          self.logger.info("获取下载文件成功")
      else:
          self.logger.info("获取下载文件失败")
          raise Exception("get download file failed")
      return True

  def ack(self):
      self.logger.info("等待一级菜单加载完成")
      WebDriverWait(self.Webdriver, 20, 0.2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#oneNav > a:nth-child(2)")))
      time.sleep(5)
      self.Webdriver.execute_script('document.querySelector("#oneNav > a:nth-child(2)").click()')
      time.sleep(5)
      self.Webdriver.execute_script('document.querySelector("#twoNav > li:nth-child(4)>ul>li:nth-child(1)").click()')
      time.sleep(10)
      #data = '{"accNo":"11-230501040008301","accName":"北京糖豆儿娱乐文化传媒有限公司","cryType":"156","cryTypNme":"人民币","orgNme":"北京分行","accChaNme":"支票户","accTypeIndex":"1","startDate":"%s","endDate":"%s","payment":"false","collection":"false","printTimeFilter":"0","isMergeBill":"0","minAmt":"","maxAmt":"","queryErBillType":"0"}' % (self.BeginDate.replace("-", ""), self.EndDate.replace("-", ""))
      data = config_request.abc_request_ack_apply
      data["accNo"] = config_account.config[self.AccountNum]["accNo"]
      data["accName"] = config_account.config[self.AccountNum]["accName"]
      data["startDate"] = self.BeginDate.replace("-", "")
      data["endDate"] = self.EndDate.replace("-", "")
      #1.发起回单异步下载请求
      self.logger.info("发起回单异步下载请求")
      result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/EReceipt/v1/submitDownload",json.dumps(data))
      try:
          response_data = json.loads(result["response"])
          self.logger.info(result["response"])
          if response_data["success"] == True:
              self.logger.info("发起回单异步下载成功")
          else:
              raise Exception("submitDownload failed")
      except Exception as e:
          self.logger.info("发起回单异步下载失败")
          raise
      #2.获得回单异步下载列表
      retryTime = 10
      uFileId = ""
      while retryTime>0:
          self.logger.info("获得回单异步下载列表")
          result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/EReceipt/v1/getDownloadList","{}")
          try:
              response_data = json.loads(result["response"])
              self.logger.info(result["response"])
              if response_data["success"] == True:
                  lastTaskId = response_data["data"]["asynErBillTaskOVOs"][0]["taskId"]
                  lastTaskStatus = response_data["data"]["asynErBillTaskOVOs"][0]["state"]
                  self.logger.info("获得回单异步下载列表,taskId=%s,state=%s"%(lastTaskId,lastTaskStatus))
                  if lastTaskStatus != "1":
                      time.sleep(30)
                      retryTime = retryTime -1
                      continue
                  else:
                      self.logger.info("下载任务状态为已完成")
                      uFileId = response_data["data"]["asynErBillTaskOVOs"][0]["ufileId"]
                      break
              else:
                  raise Exception("getDownloadList failed")
          except Exception as e:
              self.logger.info("获得回单异步下载列表失败")
              raise
      if uFileId == "":
          self.logger.info("获得最近下载任务超时")
          raise Exception("get last task state timeout!")

      data = config_request.abc_request_ack_download
      data["uFileId"] = uFileId
      #3.等待并下载最新产生的回单
      #data = '{"uFileId":"%s"}'%(uFileId)
      #1.发起回单异步下载请求
      self.logger.info("发起回单异步下载请求")
      result = self.sendHttpRequest("post", "/CorporServCloud/cfsp-access/EReceipt/v1/asynDownloadFile", json.dumps(data))
      try:
          if result["ret"] == True and result["download"]=="true":
              self.logger.info("请求下载文件成功")
              self.download()
          else:
              raise Exception("asynDownloadFile failed")
      except Exception as e:
          self.logger.info("请求下载文件失败")
          raise
      return True


  def quit(self):
      self.Webdriver.quit()
      return True