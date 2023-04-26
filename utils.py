# coding: utf-8
import json
import subprocess
import config
import os
import datetime
from decimal import *
import uiautomation as auto
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

ROOT_DOWNLOAD_PATH = config.DATA_ROOT + "download\\"


def getNowTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

if __name__ == '__main__':
    s1 = datetime.datetime.strptime("2023-01-09", "%Y-%m-%d").date()
    s2 = datetime.date.today()
    print(s1)
    print (s2)
    print (s1 < s2)





