import time
from ctypes import *
import win32api

class usbhub(object):

    def __init__(self):
        self._usbCtrl = windll.LoadLibrary('.\\usb\\usbHubCtrl-x64.dll')
        buf = (c_char * 10)()
        result = self._usbCtrl.GetDeviceList(buf, 10)
        if result == 0:
            print ("No USB Hub found, exit!")
            self._PortNum = 0
        else:
            print ("Load USBHub OK!")
            self._PortNum = buf.value[0]
        return

    def __del__(self):
        win32api.FreeLibrary(self._usbCtrl._handle)
        print("Unload USBHub!")
        return

    def openDevice(self):
        self._deviceHandle = self._usbCtrl.OpenDevice(self._PortNum)
        if self._deviceHandle<=0:
            raise Exception("Open Device Failed!")

    def closeDevice(self):
        self._usbCtrl.CloseDevice(self._deviceHandle)

    def setDeviceStatus(self, slotNum=0):
        self.openDevice()
        deviceStatus = (c_char * 30)(0)
        for i in range(0, 30):
            if slotNum - 1 == i:
                deviceStatus[i] = 1
        result = self._usbCtrl.WriteDevice(self._deviceHandle, deviceStatus, 30)
        self.closeDevice()
        return result > 0

    def switchSlot(self, slotNum, interval=0):
        self.setDeviceStatus(0)
        time.sleep(interval)
        return self.setDeviceStatus(slotNum)

    def getDeviceStatus(self):
        ret = {}
        self.openDevice()
        deviceStatus = (c_char * 30)(0)
        result =  self._usbCtrl.GetDeviceStatus(self._deviceHandle, deviceStatus, 30)
        print (deviceStatus.raw)
        for i in range(0, 30):
            if deviceStatus[i] == b'\x01':
                ret[i+1] = True
            else:
                ret[i+1] = False
        self.closeDevice()
        return ret

    def isUsbHubWorking(self):
        return not self._PortNum == 0

if __name__ == '__main__':

    for i in range(0,30):
        dd = usbhub()
        dd.getDeviceStatus()
















