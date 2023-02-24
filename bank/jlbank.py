import uiautomation
from bank.bank import Bank
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import ait
import threading
import uiautomation as auto
from DD.DDLib import DDLib


def worker(pwd):
    time.sleep(5)
    dd = DDLib()
    dd.send_keys(pwd)
    time.sleep(1)
    dd.dd_dll.DD_key(815, 1)
    dd.dd_dll.DD_key(815, 2)


class jlbank(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "JLBANK"
        self.BinPath = ""
        self.LoginUrl = "https://enetbank.jlbank.com.cn:8081/"
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
        # 防止缓存, 加入随机数
        self.Webdriver.get(self.LoginUrl + "?a=" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        self.Webdriver.maximize_window()
        self.logger.info("按tab键盘切换到密码输入框")
        self.Webdriver.find_element(By.ID, "pwdObj").send_keys(Keys.TAB)
        self.logger.info("输入登陆密码")
        self.sendkeysRemote(self.LoginPasswd)
        time.sleep(1)
        self.logger.info("点击登陆按钮")
        self.Webdriver.find_element(By.ID, "loginBtn").click()
        WebDriverWait(self.Webdriver, 15, 0.2).until(EC.url_contains("index"))
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("开始查询")
        try:
            WebDriverWait(self.Webdriver, 3, 0.2).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="outBody"]/DIV[3]/DIV/DIV[3]/BUTTON')))
            self.Webdriver.find_element(By.XPATH, '//*[@id="outBody"]/DIV[3]/DIV/DIV[3]/BUTTON').click()
            self.logger.info("发现多个证书,已关闭")
        except Exception as e:
            self.logger.info("未发现多个证书")

        self.logger.info("点击账户明细")
        self.Webdriver.find_element(By.XPATH,
                                    '//*[@id="router-view"]/DIV/DIV/DIV[4]/DIV[3]/DIV[2]/DIV/DIV/DIV[3]/DIV[3]').click()

        WebDriverWait(self.Webdriver, 10, 0.2).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="router-view"]/DIV[1]/DIV[2]/BUTTON[2]')))

        # 修改起止日期
        js = 'document.querySelectorAll(".el-date-editor.date-picker.el-input.el-input--prefix.el-input--suffix.el-date-editor--date>input")[0].value = "''"\n' \
             'document.querySelectorAll(".el-date-editor.date-picker.el-input.el-input--prefix.el-input--suffix.el-date-editor--date>input")[1].value = "''"'
        self.logger.info("修改起止日期:" + js)
        self.Webdriver.execute_script(js)
        time.sleep(1)
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    ".el-date-editor.date-picker.el-input.el-input--prefix.el-input--suffix.el-date-editor--date:first-child>input").send_keys(
            self.BeginDate)
        time.sleep(1)
        self.Webdriver.find_element(By.CSS_SELECTOR,
                                    ".el-date-editor.date-picker.el-input.el-input--prefix.el-input--suffix.el-date-editor--date:last-child>input").send_keys(
            self.EndDate)
        time.sleep(1)
        self.Webdriver.find_element(By.XPATH, '//*[@id="router-view"]/DIV[1]/DIV[2]/BUTTON[2]').click()
        self.logger.info("结束查询")
        return True

    def download(self):
        self.Webdriver.find_element(By.XPATH, '//*[@id="router-view"]/DIV[1]/DIV[3]/DIV[4]/BUTTON[1]').click()
        time.sleep(2)
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
        self.Webdriver.quit()
        return True

    def run(self):
        # time.sleep(5)
        self.login()
        self.query()
        self.download()
        self.quit()