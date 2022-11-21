#pragma once

#ifdef USBCTRL_EXPORTS

#define DLL_API _declspec(dllexport)

#else

#define DLL_API _declspec(dllimport)

#endif // DOORACCESSCTRL_EXPORTS

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

DLL_API
int _stdcall GetSWVersion(char* version, int len);

DLL_API
int _stdcall GetDeviceList(char* pDeviceList, int len);

DLL_API
int _stdcall OpenDevice(int port);

DLL_API
void _stdcall CloseDevice(int device);

DLL_API
int _stdcall GetDeviceUSBCount(int device);

DLL_API
int _stdcall GetDeviceId(int device, char* pDeviceId, int len);

DLL_API
int _stdcall GetDeviceStatus(int device, char* pStatus, int len);

DLL_API
int _stdcall WriteDevice(int device, char* pOut, int len);

#ifdef __cplusplus
}
#endif // __cplusplus
