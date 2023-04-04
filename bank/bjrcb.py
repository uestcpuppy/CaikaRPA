from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uiautomation as auto


class bjrcb(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "BJRCB"
        self.BinPath = ""
        self.LoginUrl = "http://www3.bjrcb.com/entbank/ebankLogin.html"
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
        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.Webdriver.get(self.LoginUrl)
        self.Webdriver.maximize_window()
        self.Webdriver.find_element(By.CSS_SELECTOR, 'a.btn_ukey_login').click()
        # document.querySelector("a.btn_ukey_login").click()
        self.logger.info("点击证书确认按钮")
        okButton = auto.ButtonControl(AutomationId="OkButton", Name="确定", Depth=3)
        okButton.Click()
        time.sleep(1)
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.ConfirmPasswd)
        time.sleep(1)
        self.logger.info("点击登录按钮")
        self.pressEnterRemote()
        # 等待加载首页
        WebDriverWait(self.Webdriver, 15, 0.2).until(
            EC.url_to_be("https://corporatebank.bjrcb.com/eweb/login.do?_locale=zh_CN&BankId=9999"))
        self.logger.info("结束登录")
        return True

    def query(self):
        # self.Webdriver.switch_to.parent_frame()
        self.logger.info("开始查询")
        self.logger.info("切换leftiframe")
        # WebDriverWait(self.Webdriver, 10, 0.2).until(
        #     EC.frame_to_be_available_and_switch_to_it((By.ID, "leftiframe")))
        time.sleep(3)

        self.Webdriver.switch_to.frame("leftiframe")
        self.Webdriver.execute_script('document.getElementById("ActTrsQryPre.do").click()')
        time.sleep(3)

        self.logger.info("返回主文档")
        self.Webdriver.switch_to.default_content()
        self.logger.info("切换到mainiframe")
        self.Webdriver.switch_to.frame("mainiframe")

        js = 'document.getElementById("BeginDate1").value = "' + self.BeginDate + '"\n' \
                                                                                  'document.getElementById("EndDate1").value = "' + self.EndDate + '"'
        self.logger.info("修改起止日期:" + js)
        self.Webdriver.execute_script(js)

        time.sleep(1)
        self.Webdriver.find_element(By.ID, 'doItButton').click()
        self.logger.info("完成查询")

        return True

    def download(self):
        self.logger.info("点击下载按钮")
        time.sleep(5)
        self.logger.info("下载流水")
        self.Webdriver.execute_script('DownloadActTrsQry(1)')
        time.sleep(2)
        if self.downloadFileFromIE():
            self.logger.info("下载成功")
        else:
            self.logger.info("下载失败")
            self.saveScreenShot()
        return True

    def quit(self):
        self.Webdriver.quit()
        return True

    def run(self):
        self.login()
        self.query()
        self.download()
        self.quit()