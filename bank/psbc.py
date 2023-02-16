import uiautomation
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import ait
from selenium.common.exceptions import TimeoutException
import threading
import uiautomation as auto
from DD.DDLib import DDLib


def worker(pwd):
    time.sleep(6)
    dd = DDLib()
    print("press enter")
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)
    time.sleep(3)
    dd.send_keys(pwd)
    time.sleep(1)
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)


class psbc(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "PSBC"
        self.BinPath = ""
        self.LoginUrl = "https://corpebank.psbc.com/#/login"
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

        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.logger.info("启动异步线程确认证书,输入密码,按回车")

        t = threading.Thread(target=worker, args=(self.ConfirmPasswd,), daemon=True)
        t.start()

        self.logger.info("打开登录页")
        self.Webdriver.get(self.LoginUrl)
        self.Webdriver.maximize_window()
        # closeButton = auto.ButtonControl(AutomationId="1", Depth=2, Name="确定", searchInterval=0.5)
        # if not closeButton.Exists(10, 0):
        #     raise Exception("密码控件等待超时")
        self.logger.info("点击登录框")
        self.Webdriver.find_element(By.ID, 'ukeyLogin').click()
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.LoginPasswd)
        self.logger.info("点击登录按钮")
        self.Webdriver.find_element(By.XPATH, '//*[@id="pane-ukeyLogin"]/form/button').click()
        self.logger.info("结束登录")
        return True

    def query(self):

        self.logger.info("开始查询")
        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.url_to_be("https://corpebank.psbc.com/#/index"))
        self.logger.info("点击交易明细")
        time.sleep(2)
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[1]/form/button[1]').click()
        time.sleep(3)
        # 设定启止日期: 先输入, 再点击, 再回车
        js = 'document.querySelector("#app > div > div.d2-layout-header-aside-content > div.d2-theme-container > div.d2-theme-container-main.zyl-no-scroll > div.d2-theme-container-main-layer > div.d2-theme-container-main-body > div > div > div > div.d2-container-full__body > div > form > div > div.el-form-item.daterange-yhh.dataControlysj.el-form-item--default > div > form:nth-child(1) > div > div > div > input").value = ""\n' \
             'document.querySelector("#app > div > div.d2-layout-header-aside-content > div.d2-theme-container > div.d2-theme-container-main.zyl-no-scroll > div.d2-theme-container-main-layer > div.d2-theme-container-main-body > div > div > div > div.d2-container-full__body > div > form > div > div.el-form-item.daterange-yhh.dataControlysj.el-form-item--default > div > form:nth-child(3) > div > div > div > input").value = ""'
        self.logger.info("修改起止日期")
        self.Webdriver.execute_script(js)
        time.sleep(1)
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    "#app > div > div.d2-layout-header-aside-content > div.d2-theme-container > div.d2-theme-container-main.zyl-no-scroll > div.d2-theme-container-main-layer > div.d2-theme-container-main-body > div > div > div > div.d2-container-full__body > div > form > div > div.el-form-item.daterange-yhh.dataControlysj.el-form-item--default > div > form:nth-child(1) > div > div > div > input").send_keys(
            self.BeginDate)
        time.sleep(1)
        self.pressEnterRemote()
        time.sleep(1)
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    "#app > div > div.d2-layout-header-aside-content > div.d2-theme-container > div.d2-theme-container-main.zyl-no-scroll > div.d2-theme-container-main-layer > div.d2-theme-container-main-body > div > div > div > div.d2-container-full__body > div > form > div > div.el-form-item.daterange-yhh.dataControlysj.el-form-item--default > div > form:nth-child(3) > div > div > div > input").send_keys(
            self.EndDate)
        time.sleep(1)
        self.pressEnterRemote()
        time.sleep(1)
        self.logger.info("点击查询按钮")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[2]/button[2]').click()
        # time.sleep(2)
        self.logger.info("结束查询")
        return True

    def download(self):
        self.logger.info("开始下载")
        self.logger.info("点击下载")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[1]/div[2]/div[2]/span').click()
        time.sleep(0.5)
        self.logger.info("点击excel")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[1]/div[2]/div[2]/ol/li[2]').click()
        time.sleep(0.5)
        self.logger.info("点击按照日期升序")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div[6]/div[5]/div/div[2]/span/button[1]').click()
        time.sleep(5)
        downloadFile = self.processDownloadFile()
        if downloadFile == "":
            self.logger.info("下载失败")
            self.saveScreenShot()
        else:
            self.logger.info("下载成功:" + downloadFile)
        self.logger.info("结束下载")
        return True

    def quit(self):
        self.Webdriver.quit()
        return True

    def run(self):
        # time.sleep(5)
        self.login()
        self.query()
        self.download()
        self.quit()