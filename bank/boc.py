from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uiautomation
from selenium.webdriver.common.keys import Keys
import threading
import uiautomation as auto
from DD.DDLib import DDLib
import os


def worker(pwd):
    time.sleep(5)
    dd = DDLib()
    dd.send_keys(pwd)
    time.sleep(1)
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)


def worker2(webdriver):
    time.sleep(2)
    webdriver.find_element(By.XPATH,
                           '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[2]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[1]/DIV/DIV/DIV[2]/DIV/DIV/DIV[1]/A/DIV').click()
    print("hello")


class boc(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "BOC"
        self.BinPath = ""
        self.LoginUrl = "https://netc2.igtb.bankofchina.com"
        self.LoginPasswd = LoginPasswd
        self.ConfirmPasswd = ConfirmPasswd
        # 可能有多个银行账号
        self.Account = LoginAccount
        self.DownloadPath = ""
        self.BeginDate = BeginDate
        self.EndDate = EndDate
        self.SlotNum = 0
        self.Logger = ""
        self.Browser = "IeInEdge"
        self.BatchId = BatchId
        self.SlotNum = SlotNum
        super().__init__()

    def login(self):
        self.logger.info("启动异步线程确认证书,输入密码,按回车")
        t = threading.Thread(target=worker, args=(self.ConfirmPasswd,), daemon=True)
        t.start()
        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.Webdriver.set_page_load_timeout(20)
        self.Webdriver.get(self.LoginUrl)
        # self.Webdriver.maximize_window()
        # time.sleep(5)
        # self.logger.info("输入登录密码")
        # self.sendkeysRemote(self.ConfirmPasswd)
        # # #点击密码控件
        # # uiautomation.ButtonControl(AutomationId='OkButton', Depth=3).Click()
        # uiautomation.EditControl(AutomationId='3005').Click()
        # self.logger.info("输入登录密码")
        # self.sendkeysRemote(self.ConfirmPasswd)
        # self.pressEnterRemote()
        # self.logger.info("回车确认")
        # 等待加载首页
        time.sleep(7)
        WebDriverWait(self.Webdriver, 15, 0.2).until(
            EC.url_to_be("https://netc2.igtb.bankofchina.com/#/login-page?redirect=%2Findex"))

        uiautomation.PaneControl(foundIndex=1, searchInterval=0.5, Depth=6).Click()
        self.sendkeysRemote(self.LoginPasswd)
        time.sleep(1)
        self.Webdriver.execute_script('document.querySelector("button").click()')
        self.logger.info("点击登录按钮")
        WebDriverWait(self.Webdriver, 15, 0.2).until(
            EC.url_to_be("https://netc2.igtb.bankofchina.com/#/index"))
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("开始查询")
        self.logger.info("点击工作台菜单")
        self.Webdriver.find_element(By.XPATH, '//*[@id="slider-group"]/DIV[2]/P').click()
        self.logger.info("点击下载申请链接")
        self.Webdriver.find_element(By.XPATH, '//*[@id="slider-group"]/DIV[2]/DIV[2]/DIV/DIV[4]/DIV[2]/P').click()
        self.logger.info("点击交易Checkbox")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[1]/DIV[2]/DIV/LABEL[3]/SPAN[1]/SPAN').click()
        js = 'document.getElementsByTagName("input")[9].value = "' + self.BeginDate.replace("-",
                                                                                            "/") + ' - ' + self.EndDate.replace(
            "-", "/") + '"'
        self.logger.info("修改起止日期:" + js)
        self.Webdriver.execute_script(js)
        self.logger.info("选择账户Checkbox")
        self.logger.info("点击文件类型下拉框")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[1]/DIV[3]/DIV[3]/DIV/DIV[1]/INPUT').click()
        self.logger.info("文件类型选择excel")
        self.Webdriver.execute_script(
            'document.querySelectorAll("ul.bfe-scrollbar__view.bfe-select-dropdown__list span")[22].click()')
        # self.logger.info("选择所有账户Checkbox")
        # self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[2]/DIV[2]/TABLE/THEAD/TR/TH[1]/DIV/DIV/SPAN/LABEL/SPAN/SPAN').click()
        self.logger.info("选择账户")
        self.Webdriver.execute_script(
            'document.querySelectorAll("input[type=checkbox]")[' + str(self.Index + 4) + '].click()')

        self.logger.info("点击生成下载文件按钮")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[3]/DIV/DIV/DIV/DIV/BUTTON').click()
        self.logger.info("完成查询")
        return True

    def download(self):
        time.sleep(10)
        self.logger.info("开始下载")
        self.logger.info("点击工作台菜单")
        self.Webdriver.find_element(By.XPATH, '//*[@id="slider-group"]/DIV[2]/P').click()
        self.logger.info("点击文件获取链接")
        self.Webdriver.find_element(By.XPATH, '//*[@id="slider-group"]/DIV[2]/DIV[2]/DIV/DIV[4]/DIV[1]/P').click()
        self.logger.info("下载最近产生的一个excel文件")
        self.logger.info("启动异步线程确认证书,输入密码,按回车")
        t = threading.Thread(target=worker2, args=(self.Webdriver,), daemon=True)
        t.start()
        # self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[2]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[1]/DIV/DIV/DIV[2]/DIV/DIV/DIV[1]/A/DIV').click()
        time.sleep(5)
        self.logger.info("点击菜单扩展按钮")
        saveAs = uiautomation.SplitButtonControl(Name="6", Depth=5)
        if not saveAs.Exists(6, 0.2):
            self.logger.info("无可下载的数据")
            self.saveScreenShot()
            return True
        saveAs.Click()
        self.logger.info("点击另存为按钮")
        saveAsButton = uiautomation.MenuItemControl(AutomationId="53409", searchInterval=0.5)
        saveAsButton.Click()
        self.logger.info("修改保存路径")
        dirEC = uiautomation.EditControl(AutomationId='1001')
        filePath = self.DownloadTempPath + self.BankName + "_" + self.BatchId + ".xlsx"
        dirEC.SendKeys(filePath)
        self.logger.info("点击保存")
        uiautomation.ButtonControl(AutomationId='1').Click()
        time.sleep(5)
        self.logger.info("从临时文件夹move到正式文件夹")
        downloadFile = self.processDownloadFile()
        if downloadFile == "":
            self.logger.info("下载失败")
            self.saveScreenShot()
        else:
            self.logger.info("下载成功:" + downloadFile)
        self.logger.info("结束下载")
        return True

    def quit(self):
        # self.Webdriver.quit()
        self.logger.info("退出浏览器")
        os.system("taskkill /F /IM iexplore.exe")
        return True

    def run(self):
        self.login()
        self.query()
        self.download()
        self.quit()