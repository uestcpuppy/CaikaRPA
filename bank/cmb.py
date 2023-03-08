from bank.bank import Bank
import time
import subprocess
import uiautomation as auto
import ait
import os


class cmb(Bank):
    def __init__(self, LoginPasswd, ConfirmPasswd, BeginDate, EndDate, BatchId, SlotNum, LoginAccount):
        self.BankName = "CMB"
        self.BinPath = "D:\\Bin\\Firmbank.exe"
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
        super().__init__()

    def login(self):
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
        self.logger.info("结束登录")
        return True

    def query(self):
        self.logger.info("开始查询")
        transBtn = auto.HyperlinkControl(AutomationId="btnTransaction", Name="交易明细", Depth=15)
        if transBtn.Exists(15, 0.5):
            # mainWindow.SetTopmost(True)
            transBtn.Click()
            self.logger.info("点击交易明细按钮")
        else:
            self.logger.info("未找到交易明细按钮")
        self.logger.info("设定起止日期:" + self.BeginDate + "/" + self.EndDate)
        beginEC = auto.EditControl(AutomationId='txtBeginDate')
        if not beginEC.Exists(15, 0.5):
            self.logger.info("未找到txtBeginDate控件")
            return False
        auto.EditControl(AutomationId='txtBeginDate').GetValuePattern().SetValue(self.BeginDate)
        auto.SendKeys('{Enter}')
        auto.EditControl(AutomationId='txtEndDate').GetValuePattern().SetValue(self.EndDate)
        auto.SendKeys('{Enter}')
        self.logger.info("点击查询按钮")
        auto.ButtonControl(AutomationId='btnCommonQuerySingle').Click()
        time.sleep(2)
        self.logger.info("结束查询")
        return True

    def download(self):
        self.logger.info("开始下载")
        self.logger.info("点击导出全部")
        auto.ButtonControl(AutomationId='btnExportSingleAll').Click()
        # saveWindow = auto.WindowControl(searchDepth=2, Name='文件下载')
        saveWindow = auto.WindowControl(ClassName="#32770", SubName="另存为", Depth=2)
        # 如果弹出保存对话框说明有数据
        if not saveWindow.Exists(5, 0.5):
            self.logger.info("无可下载的数据")
            self.saveScreenShot()
            return True
        # auto.ButtonControl(AutomationId='4427').Click()
        # time.sleep(3)
        self.logger.info("修改保存路径")
        dirEC = auto.EditControl(AutomationId='1001')
        filePath = self.DownloadTempPath + self.BankName + "_" + self.BatchId + ".xlsx"
        dirEC.SendKeys(filePath)
        self.logger.info("点击保存")
        auto.ButtonControl(AutomationId='1').Click()
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
        # auto.WindowControl(searchDepth=1, SubName="招商银行企业银行").GetWindowPattern().Close()
        # auto.ButtonControl(AutomationId='2020').Click()
        # time.sleep(1)
        # ait.click()
        self.logger.info("退出客户端")
        os.system("taskkill /F /IM Firmbank.exe")
        return True

    def run(self):
        self.login()
        self.query()
        self.download()
        self.quit()