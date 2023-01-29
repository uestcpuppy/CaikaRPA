import database
from usb.usbhub import usbhub
import utils
import importlib
import sys
import base64

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
        # 调用usb hub
        usb = usbhub()
        # 打开指定的端口
        usb.switchSlot(int(slotNum), 2)
        bank = slotInfo["bank"].lower()
        mod = importlib.import_module("bank."+bank)
        bankClass = getattr(mod, bank)
        bankObj = bankClass(login_pwd, confirm_pwd, beginDate, endDate, executionId, slotNum, slotInfo["login_account"])
        bankObj.run()
        database.updateExecution(executionId, status="FINISHED",runEndDatetime=utils.getNowTime())
    except Exception as e:
        database.updateExecution(executionId, status="FAILED",runEndDatetime=utils.getNowTime())
        bankObj.logger.exception(f"exception: {str(e)}")



