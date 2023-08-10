from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import database
import json
import config_request
import urllib.parse

def worker(pwd, obj):
    time.sleep(5)
    obj.sendkeysRemote(pwd)
    time.sleep(5)
    obj.pressEnterRemote()

class cib(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        super().__init__(BankName="CIB",
                         Browser="IeInEdge",
                         LoginUrl="https://corporatebank.cib.com.cn/firm/main/login.do",
                         BinPath="",
                         LoginPasswd=LoginPasswd,
                         ConfirmPasswd=ConfirmPasswd,
                         BeginDate=BeginDate,
                         EndDate=EndDate,
                         BatchId=BatchId,
                         SlotNum=SlotNum,
                         LoginAccount=LoginAccount)

    def login(self):
        self.initWebdriver()
        self.logger.info("启动异步线程确认证书,输入密码,按回车")
        t = threading.Thread(target=worker, args=(self.ConfirmPasswd,self), daemon=True)
        t.start()
        self.logger.info("开始登录 "+self.BankName+" "+ self.LoginUrl)
        self.Webdriver.get(self.LoginUrl)
        time.sleep(3)
        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.element_to_be_clickable((By.ID,"loginName")))
        time.sleep(1)
        self.logger.info("输入登录账户名")
        self.Webdriver.find_element(By.ID, 'loginName').send_keys(self.LoginAccount)
        time.sleep(1)
        self.logger.info("点击登录密码输入框")
        self.Webdriver.execute_script('document.querySelector("#password").focus()')
        time.sleep(1)
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.LoginPasswd)
        time.sleep(1)
        self.logger.info("勾选隐私条款")
        self.Webdriver.find_element(By.ID, 'privacy_check').click()
        time.sleep(1)
        self.logger.info("确认回车")
        self.pressEnterRemote()
        self.logger.info("等待首页加载完毕")
        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.url_to_be("https://corporatebank.cib.com.cn/firm/main/mainx"))
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("进入明细查询页")
        result_1 = self.sendHttpRequest("get", "/firm/query/accountQuery/queryTradeDetail.do?flag=TODAY&FUNID=130000|130100", "")
        if result_1["ret"] and result_1["response"] != "":
            self.logger.info("进入明细查询页成功")
        else:
            self.logger.info("进入明细查询页失败")
            raise Exception("detaillist get page failed!")

        self.logger.info("查询数据")
        data = config_request.cib_request_detaillist
        data["detailCond.startDate"] = self.BeginDate
        data["detailCond.endDate"] = self.EndDate
        query_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
        result_2 = self.sendHttpRequest("post", "/firm/query/accountQuery/queryTradeDetail", query_str)
        if result_2["ret"] and result_2["response"] != "":
            self.logger.info("查询数据成功")
        else:
            self.logger.info("查询数据失败")
            raise Exception("detaillist query failed!")

        self.logger.info("获取下载文件ID")
        result_3 = self.sendHttpRequest("post", "/firm/query/accountQuery/queryTradeDetail!download.do?flag=HISTORY&decorator=blank&confirm=true", "")
        if result_3["ret"] and result_3["response"] != "":
            res = result_3["response"]
            self.logger.info(result_3["response"])
            start_pos = res.find("autoOpen='") + 10
            fileId = res[start_pos:start_pos + 19]
            self.logger.info("获取下载文件ID成功:"+fileId)
            result_download = self.sendHttpRequest("get","/firm/main/download!download.do?fileNameId="+fileId,"")
            if result_download["ret"] == True and result_download["download"] == "true":
                self.logger.info("下载文件成功")
                return True
            else:
                self.logger.info("下载文件失败")
                raise Exception("download file failed!")
        else:
            self.logger.info("获取下载文件ID失败")
            raise Exception("detaillist getfileID failed!")
        return True
    def download(self):
        self.logger.info("开始下载")
        if self.downloadFileFromIE():
            self.logger.info("下载成功")
        else:
            self.logger.info("下载失败")
            self.saveScreenShot()
        return True

    def queryBalance(self):
        self.logger.info("执行js")
        result = self.sendHttpRequest("post", "/firm/main/account/commonAccount!queryBalance.do","acctNo="+self.AccountNum)
        if result["ret"] and result["response"] != "":
            response_data = json.loads(result["response"])
            self.logger.info(result["response"])
            balance = response_data["availableBalanceStr"].replace(",", "")
            if response_data["success"]:
                self.logger.info("查询余额成功:" + balance)
                database.updateExecution(executionId=self.BatchId, balance=balance)
            else:
                self.logger.info("查询余额失败")
                raise Exception("queryBalance failed!")
        else:
            self.logger.info("查询余额失败")
            raise Exception("queryBalance failed!")
        return True