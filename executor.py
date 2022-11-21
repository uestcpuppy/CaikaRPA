import time
import database
from usb.usbhub import usbhub
import sys
import datetime
import utils
from bank.citic import citic
from bank.abc import abc
from bank.icbc import icbc
from bank.spdb import spdb
from bank.cmb import cmb
from bank.ccb import ccb
from bank.cib import cib

if __name__ == '__main__':

    #参数: executionId, slotNum, beginDate, endDate
    executionId = sys.argv[1]
    slotNum = sys.argv[2]
    beginDate = sys.argv[3]
    endDate = sys.argv[4]

    slotInfo = database.getSlotInfo(slotNum)


    #任务的状态: READY, RUNNING, FINISHED, FAILED

    try:
        database.updateExecution(executionId, status="RUNNING")
        # 调用usb hub
        usb = usbhub()
        # 打开指定的端口
        usb.switchSlot(int(slotNum), 2)

        bankObj = eval(slotInfo["bank"].lower()
                       + "('" + slotInfo["login_pwd"]
                       + "','" + slotInfo["confirm_pwd"] + "','"
                       + beginDate + "','"
                       + endDate + "','"
                       + executionId + "','"
                       + slotNum + "','"
                       + slotInfo["login_account"] + "')")
        bankObj.run()
        database.updateExecution(executionId, status="FINISHED",runEndDatetime=utils.getNowTime())
    except Exception as e:
        database.updateExecution(executionId, status="FAILED",runEndDatetime=utils.getNowTime())
        bankObj.logger.exception(f"exception: {str(e)}")




