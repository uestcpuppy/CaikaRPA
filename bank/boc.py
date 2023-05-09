from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uiautomation
import threading
from DD.DDLib import DDLib
import os
import ait

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
        uiautomation.uiautomation.SetGlobalSearchTimeout(15)
        self.logger.info("启动异步线程确认证书,输入密码,按回车")
        t = threading.Thread(target=worker, args=(self.ConfirmPasswd,), daemon=True)
        t.start()
        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.Webdriver.set_page_load_timeout(20)
        self.Webdriver.get(self.LoginUrl)

        retrytimes = 15
        while retrytimes>0:
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
        time.sleep(3)
        self.logger.info("开始查询")
        self.logger.info("跳转到下载申请页")
        self.Webdriver.execute_script('window.location = "/#/work-bench/download-center/download-apply/index"')
        self.Webdriver.execute_script('window.location.reload()')
        # time.sleep(8)
        WebDriverWait(self.Webdriver, 15, 0.2).until(EC.url_to_be("https://netc2.igtb.bankofchina.com/#/work-bench/download-center/download-apply/index"))
        self.logger.info("点击交易Checkbox")
        self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[1]/DIV[2]/DIV/LABEL[3]/SPAN[1]/SPAN').click()
        js = 'document.getElementsByTagName("input")[9].value = ""\n'\
            'document.getElementsByTagName("input")[9].focus()'
        self.Webdriver.execute_script(js)
        self.sendkeysRemote(self.BeginDate.replace("-","/"))
        time.sleep(0.3)
        ait.press('SPACE')
        time.sleep(0.3)
        self.sendkeysRemote("-")
        ait.press('SPACE')
        self.sendkeysRemote(self.EndDate.replace("-","/"))
        time.sleep(1)
        ait.press('TAB')
        # js = 'document.getElementsByTagName("input")[9].value = "'+self.BeginDate.replace("-","/")+' - '+self.EndDate.replace("-","/")+'"'
        self.logger.info("修改起止日期:"+js)
        # self.Webdriver.execute_script(js)
        self.logger.info("选择账户Checkbox")
        self.logger.info("点击文件类型下拉框")
        self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[1]/DIV[3]/DIV[3]/DIV/DIV[1]/INPUT').click()
        self.logger.info("文件类型选择excel")
        self.Webdriver.execute_script('document.querySelectorAll("ul.bfe-scrollbar__view.bfe-select-dropdown__list span")[22].click()')
        # time.sleep(1000)
        # self.logger.info("选择所有账户Checkbox")
        # self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[2]/DIV[2]/DIV[2]/TABLE/THEAD/TR/TH[1]/DIV/DIV/SPAN/LABEL/SPAN/SPAN').click()
        self.logger.info("选择账户")
        self.Webdriver.execute_script('document.querySelectorAll("input[type=checkbox]")['+str(self.Index+4)+'].click()')
        self.logger.info("点击生成下载文件按钮")
        self.Webdriver.find_element(By.XPATH, '//*[@id="app"]/DIV/DIV[3]/SECTION/DIV[1]/DIV[3]/DIV/DIV/DIV[2]/DIV[1]/DIV/DIV[3]/DIV/DIV/DIV/DIV/BUTTON').click()
        self.logger.info("完成查询")
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

    def quit(self):
        self.logger.info("退出浏览器")
        os.system("taskkill /F /IM iexplore.exe")
        return True

    # def run(self):
    #     self.login()
    #     self.query()
    #     self.download()
    #     self.quit()