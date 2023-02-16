import database
from usb.usbhub import usbhub
import importlib
import sys
import base64
import time
import threading
import utils
import win32gui
from win32.lib import win32con
import win32process
import psutil

def killWindow(hwnd, extra):
    isBrowserWindow = False
    if win32gui.IsWindowVisible(hwnd):
        #判断该window是浏览器还是普通窗口
        #根据前台窗口的句柄获取线程tid和进程pid
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        # 根据前台窗口的进程pid获取进程名称
        process_name = psutil.Process(pid).name()
        # 获取窗口标题
        windowTitle = win32gui.GetWindowText(hwnd)
        if process_name=="iexplore.exe" or process_name=="msedge.exe" or process_name=="chrome.exe":
            isBrowserWindow = True
        if isBrowserWindow:
            #如果浏览器不是当前进程的子进程 且 浏览器标题不是"财咖网银助手1.0", 那么就杀掉
            current_process = psutil.Process()
            if "财咖网银助手1.0" not in windowTitle and pid not in [item.pid for item in current_process.children(recursive=True)]:
                print(str(pid))
                print("not my child: "+windowTitle)
                # print(current_process.children(recursive=True))
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        else:
            # print(windowTitle)
            # print(process_name)
            #如果是普通窗口, 符合条件的关掉
            if windowTitle=="温馨提示" and (process_name=="D4Svr_CCB.exe" or process_name=="WDCertM_CCB.exe"):
                print("温馨提示建行tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if process_name=="USBKeyTools.exe" and windowTitle=="":
                print("无名建行tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if windowTitle=="中国邮政储蓄银行" and process_name=="UKTools.exe":
                print("邮储tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def worker():
    while True:
        win32gui.EnumWindows(killWindow, None)
        # print('i am working')
        time.sleep(0.5)

if __name__ == '__main__':

    #参数: executionId, slotNum, beginDate, endDate
    executionId = sys.argv[1]
    slotNum = sys.argv[2]
    beginDate = sys.argv[3]
    endDate = sys.argv[4]
    slotInfo = database.getSlotInfo(slotNum)
    login_pwd = base64.b64decode(str.encode(slotInfo["login_pwd"])).decode()
    confirm_pwd = base64.b64decode(str.encode(slotInfo["confirm_pwd"])).decode()
    # login_pwd = slotInfo["login_pwd"]
    # confirm_pwd = slotInfo["confirm_pwd"]
    #任务的状态: READY, RUNNING, FINISHED, FAILED

    try:
        database.updateExecution(executionId, status="RUNNING")
        #启动守护进程
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        # 调用usb hub
        usb = usbhub()
        # 打开指定的端口
        usb.switchSlot(int(slotNum), 1)
        time.sleep(5)
        bank = slotInfo["bank"].lower()
        mod = importlib.import_module("bank."+bank)
        bankClass = getattr(mod, bank)
        bankObj = bankClass(login_pwd, confirm_pwd, beginDate, endDate, executionId, slotNum, slotInfo["login_account"])
        bankObj.run()
        database.updateExecution(executionId, status="FINISHED",runEndDatetime=utils.getNowTime())
    except Exception as e:
        database.updateExecution(executionId, status="FAILED",runEndDatetime=utils.getNowTime())
        bankObj.logger.exception(f"exception: {str(e)}")



