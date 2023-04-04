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
from PIL import ImageGrab
import cv2
import numpy as np
import config

def video_record():   # 录入视频
  global executionId
  filename = config.DOWNLOAD_DIR + executionId +"\\" + executionId
  screen = ImageGrab.grab() # 获取当前屏幕
  width, high = screen.size # 获取当前屏幕的大小
  fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D') # MPEG-4编码,文件后缀可为.avi .asf .mov等
  video = cv2.VideoWriter('%s.avi' % filename, fourcc, 15, (width, high)) # （文件名，编码器，帧率，视频宽高）
  #print('3秒后开始录制----')  # 可选
  #time.sleep(3)
  print('开始录制!')
  global start_time
  start_time = time.time()
  while True:
    if flag:
      print("录制结束！")
      video.release() #释放
      break
    im = ImageGrab.grab()  # 图片为RGB模式
    imm = cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR) # 转为opencv的BGR模式
    video.write(imm)  #写入

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
                utils.stopTask(pid)
        else:
            # print(windowTitle)
            # print(process_name)
            #如果是普通窗口, 符合条件的关掉
            if windowTitle=="温馨提示" and (process_name=="D4Svr_CCB.exe" or process_name=="WDCertM_CCB.exe"):
                print("温馨提示建行tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if process_name=="USBKeyTools.exe" and windowTitle=="":
                print("usbkeytools无名建行tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if process_name=="CCBCertificate.exe" and windowTitle=="":
                print("无名建行ccbcertificate tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if windowTitle=="中国邮政储蓄银行" and process_name=="UKTools.exe":
                print("邮储tips found")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            if windowTitle=="用户提示":
                print(process_name)
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

        #启动录屏线程
        # flag = False
        # th = threading.Thread(target=video_record)
        # th.start()
        # time.sleep(10)

        # 调用usb hub
        usb = usbhub()

        # 打开指定的端口
        realSlotNum =  slotNum[1:3]
        usb.switchSlot(int(realSlotNum), 1)

        time.sleep(2)
        bank = slotInfo["bank"].lower()
        mod = importlib.import_module("bank."+bank)
        bankClass = getattr(mod, bank)
        bankObj = bankClass(login_pwd, confirm_pwd, beginDate, endDate, executionId, slotNum, slotInfo["login_account"])
        bankObj.run()
        database.updateExecution(executionId, status="FINISHED",runEndDatetime=utils.getNowTime())
    except Exception as e:
        database.updateExecution(executionId, status="FAILED",runEndDatetime=utils.getNowTime())
        bankObj.logger.exception(f"exception: {str(e)}")
    finally:
        flag = True