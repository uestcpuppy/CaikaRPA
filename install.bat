@echo off
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c pushd ""%~dp0"" && ""%~s0"" ::","","runas",1)(window.close)&&exit
echo ����python��������
setx PATH "D:\caika\python37;D:\caika\python37\Scripts;%PATH%;" /m
echo ��mysql����Ϊϵͳ����
D:\caika\mysql-8.0.31\bin\mysqld --install
echo ����mysql
net start mysql
echo �������ű����Ƶ�����
set d=%USERPROFILE%\Desktop
copy D:\caika\rpa\caika.bat %d%
echo �ƿ��������ְ�װ���,  ��������caikaͼ������ϵͳ!
@pause