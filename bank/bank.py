from selenium import webdriver
import time
import os.path
import ait
import logging
import os
import win32con
import win32api
import database
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from DD.DDLib import DDLib
import shutil
import requests
import uiautomation as auto
import config
import pyscreenshot

class Bank:
    def __init__(self):
        '所有网银处理的基类'
        self.BankName = ""
        # self.BinPath = ""
        # self.LoginUrl = ""
        # self.LoginPasswd = ""
        # self.ConfirmPasswd = ""
        # # 可能有多个银行账号
        # self.Accounts = ""
        self.DownloadPath = config.DATA_ROOT
        self.DownloadTempPath = config.DOWNLOAD_TEMP_DIR
        # self.BeginDate = ""
        # self.EndDate = ""
        # # 1.today 2.lastday 3.last7days 4.last14days 5.last30days
        # self.DateType = ""
        # self.SlotNum = 0
        # self.Logger = ""
        # #webdriver
        # self.Webdriver = ""
        # #IE, Chrome
        # self.Browser = ""
        #关闭CCB
        self.closeCCBTips()
        self.DDServer = "127.0.0.1:8888"
        if self.Browser != "":
            self.initWebdriver()
        self.initLogger()
        self.clearTempDownloadDir()
        self.initDownloadDir()
        self.xlsFileName = ""
        self.imgFileName = ""

    def initDownloadDir(self):
        targetDir = config.DOWNLOAD_DIR + self.BatchId + "\\"
        if not os.path.exists(targetDir):
            os.mkdir(targetDir)
        return

    def login(self):
        return True
    def query(self):
        return True
    def download(self):
        return True
    def quit(self):
        return True
    def initLogger(self):
        # 第一步：创建日志器
        logger = logging.getLogger()
        if logger.handlers:
            self.logger = logging
            return
        logger.level = logging.INFO
        # 第二步：定义处理器。控制台和文本输出两种方式
        console_handler = logging.StreamHandler()
        file_path = "./back.log"
        if os.path.exists(file_path):
            mode = 'a'
        else:
            mode = 'w'
        file_handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
        # 第三步：设置的不同的输入格式
        console_fmt ='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        file_fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        # 第三步：格式
        fmt1 = logging.Formatter(fmt=console_fmt)
        fmt2 = logging.Formatter(fmt=file_fmt)
        # 第四步:把格式传给处理器
        console_handler.setFormatter(fmt1)
        file_handler.setFormatter(fmt2)
        # 第五步:把处理器传个日志器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        self.logger = logging

    def initWebdriver(self):
        if self.Browser == "Chrome":
            options = webdriver.ChromeOptions()
            prefs = {
                'profile.default_content_settings.popups': 0,
                'download.default_directory': self.DownloadTempPath
            }
            options.add_experimental_option('prefs', prefs)
            # options.add_argument("--headless")

            options.add_experimental_option("excludeSwitches", ['enable-automation'])
            desired_capabilities = DesiredCapabilities.CHROME
            # 修改页面加载策略
            # none表示将br.get方法改为非阻塞模式，在页面加载过程中也可以给br发送指令，如获取url，pagesource等资源。
            desired_capabilities["pageLoadStrategy"] = "none"
            # self.Webdriver = webdriver.Chrome(chrome_options=options)
            #浦发需要这种模式
            self.Webdriver = webdriver.Chrome(chrome_options=options, desired_capabilities=desired_capabilities)
        elif self.Browser == "Ie":
            self.Webdriver = webdriver.Ie()
        elif self.Browser == "Edge":
            self.Webdriver = webdriver.Edge()
        elif self.Browser == "IeInEdge":
            ie_options = webdriver.IeOptions()
            ie_options.ignore_zoom_level = True
            ie_options.attach_to_edge_chrome = True
            ie_options.edge_executable_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            ie_options.page_load_strategy = "none"
            # driver = webdriver.Ie(executable_path=r"D:\\Python37\\Scripts\\IEDriverServer.exe", options=ie_options)
            driver = webdriver.Ie(options=ie_options)
            self.Webdriver = driver

        self.Webdriver.maximize_window()
        #find_element隐式等待时间
        self.Webdriver.implicitly_wait(config.IMPLICITLY_WAIT)
        #js脚本执行超时时间
        self.Webdriver.set_script_timeout(config.SCRIPT_TIMEOUT)

    def highlight(self,element):
        self.Webdriver.execute_script("arguments[0].setAttribute('style', "
                                      "arguments[1]);",
                                      element,"background: yellow; border: 5px solid red;")
    def pressAit(self,str):
        for i in str:
            ait.press(i)
            time.sleep(0.3)
    def pressAltS(self):
        time.sleep(1)
        # alt+s快捷键
        win32api.keybd_event(0x12, 0, 0, 0)  # 按下alt
        win32api.keybd_event(83, 0, 0, 0)  # 按下s
        win32api.keybd_event(83, 0, win32con.KEYEVENTF_KEYUP, 0)  # 松开s
        win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)  # 松开al
        return True
    def pressEnterDD(self):
        dd = DDLib()
        dd.dd_dll.DD_key(815, 1)
        dd.dd_dll.DD_key(815, 2)
        return True
    def pressDD(self, str):
        dd = DDLib()
        dd.send_keys(str)
        return True

    def sendkeysRemote(self, str):
        url =  "http://"+self.DDServer + "/action=sendkeys&str="+str
        ret = requests.get(url)

    def pressEnterRemote(self):
        url =  "http://"+self.DDServer + "/action=enter"
        ret = requests.get(url)

    def killIeRemote(self):
        url =  "http://"+self.DDServer + "/action=killie"
        ret = requests.get(url)

    def killCcbRemote(self):
        url =  "http://"+self.DDServer + "/action=killccb"
        ret = requests.get(url)

    #此方法用于下载完成后对文件的处理
    def processDownloadFile(self):
        #检查临时文件夹下是否有文件
        tempFile = self.getFirstFileName(self.DownloadTempPath, False)
        if tempFile == "":
            return ""
        else:
            #截取扩展名
            tempIndex = tempFile.find(".")
            fileExt = tempFile[tempIndex:]
            targetDir = config.DOWNLOAD_DIR + self.BatchId+"\\"
            fileName = self.BankName + "_" + self.BatchId + fileExt
            targetFile = targetDir + fileName
            shutil.move(self.DownloadTempPath +"\\"+tempFile, targetFile)
            database.updateExecution(self.BatchId, xlsFilename=fileName)
            return targetFile

    def isFileExist(self, filePath):
        return os.path.exists(filePath)

    def clearTempDownloadDir(self):
        shutil.rmtree(self.DownloadTempPath)
        os.mkdir(self.DownloadTempPath)

    def getFirstFileName(self, fileDir, fullPath=True):
        file_list = os.listdir(fileDir)
        if len(file_list) == 1:
            if fullPath:
                return fileDir + "\\" + file_list[0]
            else:
                return file_list[0]
        else:
            return ""

    def saveScreenShot(self):
        image = pyscreenshot.grab()
        targetDir = config.DOWNLOAD_DIR + self.BatchId + "\\"
        fileName = self.BankName + "_" + self.BatchId + ".png"
        targetFile = targetDir + fileName
        image.save(targetFile)
        database.updateExecution(self.BatchId, imgFilename=fileName)

    def closeCCBTips(self):
        closeButton = auto.PaneControl(Name="温馨提示", Depth=1, searchInterval=0.5)
        if closeButton.Exists(2, 0):
            closeButton.SetActive()
            closeButton.Click(y=-50)

    def waitElementLoad(self, webdriver, byWhich, elementValue, seconds):
        for i in range(seconds * 5):
            try:
                webdriver.find_element(byWhich, elementValue)
            except Exception as e:
                # print("尚未找到",elementValue)
                time.sleep(0.2)
            else:
                # print("已经找到")
                return True
        raise Exception("WaitElement timeout")

    def waitSwitchFrame(self, webdriver, byWhich, elementValue, seconds):
        for i in range(seconds * 5):
            try:
                webdriver.switch_to.frame(webdriver.find_element(byWhich, elementValue))
            except Exception as e:
                # print("尚未切换",elementValue)
                time.sleep(0.2)
            else:
                # print("已经切换")
                return True
        raise Exception("SwitchFrame timeout")

if __name__ == '__main__':
    a = Bank()
    r = a.processDownloadFile()
    print (r)






