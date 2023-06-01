from bank.bank import Bank
# from bank import Bank
import time
import subprocess
import uiautomation as auto
import os
from selenium import webdriver
import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database

class cmb(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "CMB"
        self.BinPath = config.CMB_BIN_PATH
        self.LoginUrl = ""
        self.LoginPasswd = LoginPasswd
        self.ConfirmPasswd = ConfirmPasswd
        # 可能有多个银行账号
        self.Accounts = ""
        self.DownloadPath = ""
        self.BeginDate = BeginDate
        self.EndDate = EndDate
        self.SlotNum = 0
        self.Logger = ""
        self.Browser = ""
        self.BatchId = BatchId
        self.SlotNum = SlotNum
        # self.logger.info("清空进程")
        os.system("taskkill /F /IM Firmbank.exe")
        super().__init__()

    def login(self):
        #初始化webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        # options.add_argument('--disable-extensions')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--remote-debugging-port=9222')  # 指定调试端口
        options.binary_location = self.BinPath  # 应用程序的路径
        #符合招行客户端版本的chromedriver
        self.Webdriver = webdriver.Chrome(executable_path=config.CMD_DRIVER_PATH, options=options)
        self.Webdriver.implicitly_wait(config.IMPLICITLY_WAIT)
        self.logger.info("开始登录 " + self.BankName + " " + self.BinPath)
        # 打开网银客户端
        subprocess.Popen(self.BinPath)
        loginWindow = auto.WindowControl(searchDepth=1, Name='联机登录')
        if loginWindow.Exists(15, 0.5):
            loginWindow.SetTopmost(True)
            self.logger.info("打开网银客户端成功")
        else:
            self.logger.info("打开网银客户端失败")
            raise Exception("打开网银客户端失败")
        # 等待U盾加载完成, 超时时间5秒
        leftTime = 10
        while leftTime > 0:
            if loginWindow.EditControl(foundIndex=1).GetValuePattern().Value != "":
                break
            self.logger.info("未检测到U盾")
            time.sleep(1)
            leftTime = leftTime - 1
        if loginWindow.EditControl(foundIndex=1).GetValuePattern().Value == "":
            raise Exception("未检测到U盾")
        if self.Index != 0:
            loginWindow.ComboBoxControl().Click()
            for i in range(self.Index):
                auto.SendKey(auto.Keys.VK_DOWN)
                time.sleep(1)
        self.logger.info("输入登录密码")
        ed = loginWindow.EditControl(foundIndex=2)
        ed.Click()
        ed.SendKeys(self.LoginPasswd, charMode=False)
        self.logger.info("输入证书密码")
        ed = loginWindow.EditControl(foundIndex=3)
        ed.Click()
        ed.SendKeys(self.ConfirmPasswd, charMode=False)
        self.logger.info("点击登录")
        loginWindow.ButtonControl(searchDepth=2, AutomationId='2020').Click()
        mainWindow = auto.WindowControl(searchDepth=1, SubName="招商银行企业银行")
        if mainWindow.Exists(15, 0.5):
            # mainWindow.SetTopmost(True)
            mainWindow.Maximize()
            self.logger.info("打开主窗口成功")
        else:
            self.logger.info("打开主窗口失败")
            raise Exception("打开主窗口失败")
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("开始查询")
        self.Webdriver.switch_to.window(self.Webdriver.window_handles[1])
        self.logger.info("点击交易明细")
        self.Webdriver.find_element(By.ID, 'btnTransaction').click()
        self.logger.info("等待查询页加载完成后切换至查询窗口")
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.number_of_windows_to_be(7))
        self.Webdriver.switch_to.window(self.Webdriver.window_handles[6])
        self.logger.info("设定起止日期:" + self.BeginDate + "/" + self.EndDate)
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, "txtBeginDate")))
        # 修改起止日期
        js = 'document.querySelector("#txtBeginDate").value = "' + self.BeginDate + '"\n'\
            'document.querySelector("#txtEndDate").value = "' + self.EndDate + '"'
        self.Webdriver.execute_script(js)
        self.logger.info("点击查询按钮")
        self.Webdriver.find_element(By.ID, 'btnCommonQuerySingle').click()
        self.logger.info("结束查询")
        return True

    def download(self):
        self.logger.info("开始下载")
        self.logger.info("点击导出全部")
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.element_to_be_clickable((By.ID, "btnExportSingleAll")))
        self.Webdriver.find_element(By.ID, 'btnExportSingleAll').click()
        if self.saveAsWindowsDialogFile():
            self.logger.info("下载成功")
        else:
            self.logger.info("下载失败")
            raise Exception("下载失败")

    def queryBalance(self):
        self.logger.info("切换窗口")
        self.Webdriver.switch_to.window(self.Webdriver.window_handles[1])
        self.logger.info("点击交易明细")
        self.Webdriver.find_element(By.ID, 'btnTransaction').click()
        self.logger.info("等待查询页加载完成后切换至查询窗口")
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.number_of_windows_to_be(7))
        self.Webdriver.switch_to.window(self.Webdriver.window_handles[6])
        self.Webdriver.find_element(By.ID, 'btnQueryAccountSingle').click()
        self.logger.info("查询账户余额")
        # WebDriverWait(self.Webdriver, 10, 0.2).until(
        #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div[5]/div/div[2]/iframe')))
        fr = self.Webdriver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/iframe')
        self.Webdriver.switch_to.frame(fr)
        WebDriverWait(self.Webdriver, 10, 0.2).until(EC.visibility_of_element_located((By.ID, 'spanACCNBR')))
        accountStr = self.Webdriver.find_element(By.ID, 'spanACCNBR').text
        balanceStr = self.Webdriver.find_element(By.ID, 'spanONLBLV').text
        balanceStr = balanceStr.replace(",", "").replace("元", "").strip()
        # self.AccountNum = "311902472710501"
        if accountStr.find(self.AccountNum) != -1:
            self.logger.info("查询余额成功:" + balanceStr)
            database.updateExecution(executionId=self.BatchId, balance=balanceStr)
        else:
            self.logger.info("查询余额失败: 未找到对应账户数据")
        return True

    def quit(self):
        self.logger.info("退出客户端")
        os.system("taskkill /F /IM Firmbank.exe")
        return True