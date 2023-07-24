# coding: utf-8
import json
import subprocess
import config
import os
import datetime
import smtplib
from email.mime.text import MIMEText
import pyscreenshot
from datetime import datetime

ROOT_DOWNLOAD_PATH = config.DATA_ROOT + "download\\"


def getNowTime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def runTask(executionId, slotNum, beginDate, endDate):
    p = subprocess.Popen("python executor.py "+executionId+" "+slotNum+" "+beginDate+" "+endDate)
    return p.pid

def stopTask(pid):
    cmd = os.popen("taskkill /F /PID "+str(pid))
    return True

def getBillDownloadFileName(fileDir, batchId):
    if batchId == "0":
        return "NULL"
    file_list = os.listdir(fileDir)
    for i in file_list:
        if (os.path.splitext(i)[1] == '.xlsx' or os.path.splitext(i)[1] == '.xls') and i.find(batchId)!=-1:
            filePath = fileDir + "\\" + i
            return filePath
    return "NULL"

def getPhotoDownloadFileName(fileDir, batchId):
    if batchId == "0":
        return "NULL"
    file_list = os.listdir(fileDir)
    for i in file_list:
        if (os.path.splitext(i)[1] == '.png' or os.path.splitext(i)[1] == '.jpg') and i.find(batchId)!=-1:
            filePath = fileDir + "\\" + i
            return i
    return "NULL"

def getBillDownloadFile(SlotNum, BatchId):
    tempPath = ROOT_DOWNLOAD_PATH + "slot_" + SlotNum
    tempFile = getBillDownloadFileName(tempPath, BatchId)
    if tempFile == "NULL":
        return "NULL"
    else:
        return "/slot_"+SlotNum+"/"+tempFile

def getPhotoDownloadFile(SlotNum, BatchId):
    tempPath = ROOT_DOWNLOAD_PATH + "slot_" + SlotNum
    tempFile = getPhotoDownloadFileName(tempPath, BatchId)
    if tempFile == "NULL":
        return "NULL"
    else:
        return "/slot_"+SlotNum+"/"+tempFile

def getLastLog(filePath, lastCount=500):
    log = open(filePath, "r", encoding='GBK')
    lines = log.readlines()
    total = len(lines)
    log.close()
    if lastCount>total:
        return "".join(lines)
    else:
        return "".join(lines[(total-lastCount):])


def sendMail(receiver, title, content):

    # 设置SMTP服务器地址、端口号、发件人邮箱账号、发件人邮箱密码、收件人邮箱账号
    smtp_server = 'smtp.qq.com'
    smtp_port = 465
    sender = '443652788@qq.com'
    sender_password = 'lquucexxepikcaib'
    receiver = 'chenxi@caikazx.com'

    # 创建邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = title

    # 连接到SMTP服务器并登录
    smtpObj = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtpObj.login(sender, sender_password)
    # 发送邮件
    smtpObj.sendmail(sender, [receiver], msg.as_string())
    # 断开与SMTP服务器的连接
    smtpObj.quit()

def saveScreenShot(executionId):
    image = pyscreenshot.grab()
    targetDir = config.DOWNLOAD_DIR
    fileName = datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f')[:-3] + ".png"
    targetFile = targetDir + fileName
    image.save(targetFile)

def RemoveAllCertsShell():
    # 设置PowerShell命令
    command = """Get-ChildItem cert:\CurrentUser\My | 
               ForEach-Object {
               $store = Get-Item $_.PSParentPath 
               $store.Open('ReadWrite') 
               $store.Remove($_) 
               $store.Close()}"""

    # 调用PowerShell并执行命令
    process = subprocess.Popen(['powershell', '-command', command], stdout=subprocess.PIPE)
    # 获取命令输出
    output = process.communicate()[0]
    return len(output) == 0

if __name__ == '__main__':
    # s1 = datetime.datetime.strptime("2023-01-09", "%Y-%m-%d").date()
    # s2 = datetime.date.today()
    # sendMail("chenxi@caikazx.com", "test", "hello")
    saveScreenShot("1911")




