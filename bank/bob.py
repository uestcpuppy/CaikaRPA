from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys

class bob(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "BOB"
        self.BinPath = ""
        self.LoginUrl = "https://cbank.bankofbeijing.com.cn/bccb/corporbank/safelogon.jsp"
        self.LoginPasswd = LoginPasswd
        self.ConfirmPasswd = ConfirmPasswd
        # 可能有多个银行账号
        self.Account = LoginAccount
        self.DownloadPath = ""
        self.BeginDate = BeginDate
        self.EndDate = EndDate
        self.SlotNum = 0
        self.Logger = ""
        self.Browser = "Edge"
        self.BatchId = BatchId
        self.SlotNum = SlotNum

        super().__init__()

    def login(self):
        self.logger.info("开始登录 " + self.BankName + " " + self.LoginUrl)
        self.Webdriver.get(self.LoginUrl)
        self.Webdriver.maximize_window()
        self.logger.info("等待jumpBtn加载完成")

        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.element_to_be_clickable((By.ID, 'txtPass')))
        self.logger.info("点击证书密码控件")
        self.Webdriver.find_element(By.ID, 'txtPass').click()
        # time.sleep(1)
        self.logger.info("输入证书密码")
        self.sendkeysRemote(self.ConfirmPasswd)
        # time.sleep(1)
        self.logger.info("点击用户名控件")
        self.Webdriver.find_element(By.ID, 'userId').click()
        # time.sleep(1)
        self.logger.info("输入用户名")
        self.sendkeysRemote(self.Account)
        # time.sleep(1)
        self.logger.info("点击登录密码控件")
        self.Webdriver.find_element(By.ID, '_ocx_password').click()
        # time.sleep(1)
        self.logger.info("输入登录密码")
        self.sendkeysRemote(self.LoginPasswd)
        time.sleep(1)
        self.logger.info("点击登录按钮")
        self.Webdriver.find_element(By.CSS_SELECTOR, 'a.login_btn').click()
        self.logger.info("等待登录页加载完成")
        WebDriverWait(self.Webdriver, 15, 0.2).until(
            EC.url_to_be("https://cbank.bankofbeijing.com.cn/bccb/corporbank/logon.jsp"))
        self.logger.info("结束登录")
        # time.sleep(1000)
        return True

    def query(self):

        self.logger.info("开始查询")

        try:
            WebDriverWait(self.Webdriver, 3, 0.2).until(EC.element_to_be_clickable((By.ID, 'skip')))
            self.Webdriver.find_element(By.ID, 'skip').click()
        except Exception as e:
            self.logger.info("未出现skip页")

        self.logger.info("切换到tranFrame")
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "tranFrame")))
        time.sleep(3)
        self.logger.info("等待明细查询按钮")
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                 'body>div>div>div>div>div>section>div>div>div>div.main-content>div>div:nth-child(1)>div.common>div.content>div>div:nth-child(3)>p')))
        self.logger.info("点击明细查询按钮")
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    'body>div>div>div>div>div>section>div>div>div>div.main-content>div>div:nth-child(1)>div.common>div.content>div>div:nth-child(3)>p').click()
        time.sleep(2)

        self.logger.info("点击开始日期")
        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        '#accountDetail > div.header > form > div.header-content > div:nth-child(3) > div > div > input:nth-child(2)')))

        if self.Index != 0:
            self.logger.info("选择账户")
            inputElement = self.Webdriver.find_element(By.XPATH,
                                                       '//*[@id="accountDetail"]/div[1]/form/div[1]/div[2]/div/div/div[1]/input')
            inputElement.click()
            time.sleep(1)
            self.Webdriver.find_element(By.CSS_SELECTOR,
                                        "body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li.el-select-dropdown__item:nth-child(" + str(
                                            self.Index + 1) + ")> span").click()
            time.sleep(2)

        # 去掉readonly属性
        self.logger.info("去掉readonly属性")
        beginDateInput = "#accountDetail > div.header > form > div.header-content > div:nth-child(3) > div > div > input:nth-child(2)"
        endDateInput = "#accountDetail > div.header > form > div.header-content > div:nth-child(3) > div > div > input:nth-child(4)"
        self.Webdriver.execute_script('document.querySelector("' + beginDateInput + '").readOnly = false')
        self.Webdriver.execute_script('document.querySelector("' + endDateInput + '").readOnly = false')
        self.Webdriver.find_element(By.CSS_SELECTOR, endDateInput).send_keys(Keys.SHIFT, Keys.TAB)
        self.sendkeysRemote(self.BeginDate)
        self.Webdriver.find_element(By.CSS_SELECTOR, beginDateInput).send_keys(Keys.TAB)
        self.sendkeysRemote(self.EndDate)
        self.Webdriver.find_element(By.CSS_SELECTOR, endDateInput).send_keys(Keys.TAB)
        time.sleep(1)
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    "#accountDetail > div.header > form > div.el-form-item > div > div > div > button.el-button.el-button--confirm").click()
        time.sleep(2)
        self.logger.info("结束查询")
        return True

    def download(self):
        self.logger.info("开始下载")
        self.logger.info("点击下载按钮")
        time.sleep(2)
        try:
            WebDriverWait(self.Webdriver, 3, 0.2).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="accountDetail"]/div[2]/div[1]/div/button[3]')))
        except Exception as e:
            self.logger.info("查询结果为空")
            self.saveScreenShot()
            return True

        self.Webdriver.find_element(By.XPATH, '//*[@id="accountDetail"]/div[2]/div[1]/div/button[3]').click()
        time.sleep(1)
        self.Webdriver.find_element(By.XPATH, '//*[@id="accountDetail"]/div[7]/div/div[3]/div/button[1]').click()
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