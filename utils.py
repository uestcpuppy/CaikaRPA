# coding: utf-8
import json
import subprocess
import config
import os
import datetime
from decimal import *
import uiautomation as auto

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
    log = open(filePath, "r", encoding='UTF8')
    lines = log.readlines()
    total = len(lines)
    log.close()
    if lastCount>total:
        return "".join(lines)
    else:
        return "".join(lines[(total-lastCount):])

if __name__ == '__main__':
    closeButton = auto.PaneControl(Name="温馨提示", Depth=1, searchInterval=0.2)
    if closeButton.Exists(5, 0.2):
        closeButton.SetActive()
        closeButton.Click(y=-50)
    else:
        print ("not found")
        print ("test")





