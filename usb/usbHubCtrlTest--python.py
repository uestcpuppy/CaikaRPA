import time
from ctypes import *



for i in range(0,1):
	usbCtrl = windll.LoadLibrary('C:\\test\\usbHubCtrl-x64.dll')
	buf = (c_char * 10)()
	serialPortNum = usbCtrl.GetDeviceList(buf, 10)
	print(serialPortNum)
	print(buf.raw)

	if serialPortNum == 0:
		print("no devcies is found, exit")
		exit(1)

	deviceStatus = (c_char * 30)()
	deviceHandle = usbCtrl.OpenDevice(buf.value[0])

	result = usbCtrl.GetDeviceStatus(deviceHandle, deviceStatus, 30)
	print (deviceStatus.raw)
	# result = usbCtrl.GetDeviceStatus(deviceHandle, deviceStatus, 30)
	# print (deviceStatus.raw)
	exit(0)

	print (buf.value[0])

	print(deviceHandle)

	print ("hello")

	deviceStatus = (c_char * 30)()
	result = usbCtrl.GetDeviceStatus(deviceHandle, deviceStatus, 30)

	print(result)
	print(deviceStatus.raw)

	deviceStatus = (c_char * 30)(0)
	deviceStatus[i] = 1
	result = usbCtrl.WriteDevice(1, deviceStatus, 30)

	# usbCtrl.CloseDevice(deviceHandle)



exit(0)


buf = (c_char * 64)()

usbCtrl.GetSWVersion(buf, 64)

print(buf.value)

buf = (c_char * 10)()

serialPortNum = usbCtrl.GetDeviceList(buf, 10)

print(serialPortNum)
print(buf.raw)

if serialPortNum == 0:
	print("no devcies is found, exit")
	exit(1)

deviceHandle = usbCtrl.OpenDevice(buf.value[0])

print(deviceHandle)



usbPortNum = usbCtrl.GetDeviceUSBCount(deviceHandle)


print(usbPortNum)

deviceId = (c_char * 10)()
result = usbCtrl.GetDeviceId(deviceHandle, deviceId, 10)

print(result)
print(deviceId.raw)

deviceStatus = (c_char * 30)()
result = usbCtrl.GetDeviceStatus(deviceHandle, deviceStatus, 30)

print(result)
print(deviceStatus.raw)

deviceStatus = (c_char * 30)(0)
deviceStatus[0] = 1
deviceStatus[1] = 0
deviceStatus[2] = 0
deviceStatus[3] = 0
deviceStatus[4] = 0
deviceStatus[5] = 0
deviceStatus[6] = 0
deviceStatus[7] = 0
deviceStatus[8] = 0
deviceStatus[9] = 0
result = usbCtrl.WriteDevice(deviceHandle, deviceStatus, 30)

print(deviceStatus.raw)
print(result)
exit(0)
deviceStatus = (c_char * 30)()
result = usbCtrl.GetDeviceStatus(deviceHandle, deviceStatus, 30)
print(result)
print(deviceStatus.raw)

usbCtrl.CloseDevice(buf.value[0])
