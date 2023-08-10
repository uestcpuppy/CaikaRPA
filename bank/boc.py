from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uiautomation
import threading
from DD.DDLib import DDLib
import os
import database
import config_request
import config_account
import json


def worker(pwd):
    win = uiautomation.WindowControl(searchDepth=3, SubName="密码")
    if win.Exists(6, 0.2):
        win.Click()
    else:
        raise Exception("未弹出密码框")
    dd = DDLib()
    dd.send_keys(pwd)
    time.sleep(1)
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)

def worker2(webdriver):
    webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[2]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[1]/DIV/DIV/DIV[2]/DIV/DIV/DIV[1]/A/DIV').click()


class boc(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        super().__init__(BankName="BOC",
                         Browser="IeInEdge",
                         LoginUrl="https://netc2.igtb.bankofchina.com",
                         BinPath="",
                         LoginPasswd=LoginPasswd,
                         ConfirmPasswd=ConfirmPasswd,
                         BeginDate=BeginDate,
                         EndDate=EndDate,
                         BatchId=BatchId,
                         SlotNum=SlotNum,
                         LoginAccount=LoginAccount)

    def login(self):
        uiautomation.uiautomation.SetGlobalSearchTimeout(15)
        # self.logger.info("启动异步线程确认证书,输入密码,按回车")
        # t = threading.Thread(target=worker, args=(self.ConfirmPasswd,), daemon=True)
        # t.start()
        self.initWebdriver()
        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.Webdriver.set_page_load_timeout(20)
        self.Webdriver.get(self.LoginUrl)
        retrytimes = 15
        while retrytimes > 0:
            win = uiautomation.WindowControl(searchDepth=1, SubName='企业网银')
            win.PaneControl(foundIndex=1, searchInterval=0.2, Depth=5).SendKeys('{Tab}')
            focused_control = uiautomation.GetFocusedControl()
            if focused_control.ClassName == "Edit":
                break
            retrytimes = retrytimes - 1
            time.sleep(1)
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.LoginPasswd)
        time.sleep(1)
        self.Webdriver.execute_script('document.querySelector("button").click()')
        self.logger.info("点击登录按钮")
        WebDriverWait(self.Webdriver, 15, 0.2).until(EC.url_to_be("https://netc2.igtb.bankofchina.com/#/index"))
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("开始申请流水下载")
        data = config_request.boc_request_detaillist_apply
        data["params"]["actIdList"][0]["actId"] = config_account.config[self.AccountNum]["actId"]
        data["params"]["startDate"] = self.BeginDate.replace("-", "/")
        data["params"]["endDate"] = self.EndDate.replace("-", "/")
        result = self.sendHttpRequest("post", "/igtb-web/_bfwajax.do?method=ActTransQueryDownload&_locale=zh_CN", "json="+json.dumps(data))
        if result["ret"] and result["response"] != "":
            response_data = json.loads(result["response"])
            self.logger.info(result["response"])
            biz_result = response_data["result"]["result"]
            if biz_result == "Y":
                self.logger.info("申请流水下载成功")
            else:
                raise Exception("detaillist apply failed!")
        else:
            self.logger.info("申请流水下载失败")
            raise Exception("detaillist apply failed!")
        return True

    def download(self):
        time.sleep(10)
        self.logger.info("开始下载")
        self.logger.info("跳转到文件下载页")
        self.Webdriver.execute_script('window.location = "/#/work-bench/download-center/file-gain/index"')
        self.Webdriver.execute_script('window.location.reload()')
        xpath = '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[2]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[1]/DIV/DIV/DIV[2]/DIV/DIV/DIV[1]/SPAN'
        WebDriverWait(self.Webdriver, 15, 0.2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if not self.Webdriver.find_element(By.XPATH, xpath).text == "未下载":
            self.logger.info("下载数据未在规定时间产生")
            self.saveScreenShot()
            return True
        self.logger.info("启动异步线程点击文件，下载最近产生的一个excel文件")
        t = threading.Thread(target=worker2, args=(self.Webdriver,), daemon=True)
        t.start()
        time.sleep(3)
        # self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[2]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[1]/DIV/DIV/DIV[2]/DIV/DIV/DIV[1]/A/DIV').click()
        if self.downloadFileFromIE():
            self.logger.info("下载成功")
        else:
            self.logger.info("下载失败")
            self.saveScreenShot()
        return True

    def queryBalance(self):
        self.logger.info("等待页面加载完成")
        time.sleep(5)
        # self.logger.info("等待一级菜单加载完成")
        # WebDriverWait(self.Webdriver, 20, 0.2).until(
        #     EC.visibility_of_element_located((By.CSS_SELECTOR, "#oneNav > a:nth-child(2)")))
        self.logger.info("执行js")
        data = config_request.boc_request_balance
        data["params"]["accountIdList"][0]["actId"] = config_account.config[self.AccountNum]["actId"]
        result = self.sendHttpRequest("post", "/igtb-web/_bfwajax.do?method=ActTodayBalanceQuery&_locale=zh_CN", "json="+json.dumps(data))

        if result["ret"] and result["response"] != "":
            response_data = json.loads(result["response"])
            self.logger.info(result["response"])
            balance = response_data["result"]["List"][0]["ATB"]["avlBalance"]
            self.logger.info("查询余额成功:" + balance)
            database.updateExecution(executionId=self.BatchId, balance=balance)
        else:
            self.logger.info("查询余额失败")
            raise Exception("queryBalance failed!")
        return True

    def quit(self):
        self.logger.info("退出浏览器")
        os.system("taskkill /F /IM iexplore.exe")
        return True