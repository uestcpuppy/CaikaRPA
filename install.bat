@echo off
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c pushd ""%~dp0"" && ""%~s0"" ::","","runas",1)(window.close)&&exit
echo ��һ���޸�ע���
regedit /s chrome.reg
echo.
echo ����������python��������
setx PATH "D:\caika\python37;D:\caika\python37\Scripts;%PATH%;" /m
echo.
echo ��������mysql����Ϊϵͳ����
D:\caika\mysql-8.0.31\bin\mysqld --install
echo.
echo ���ġ�����mysql
net start mysql
echo.
echo ���塿�������ű����Ƶ�����
set d=%USERPROFILE%\Desktop
copy D:\caika\rpa\*.lnk %d%
echo.
echo �ƿ��������ְ�װ���,  ��������caikaͼ������ϵͳ!
@pause