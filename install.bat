@echo off
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c pushd ""%~dp0"" && ""%~s0"" ::","","runas",1)(window.close)&&exit
echo 【一】修改注册表
regedit /s chrome.reg
echo.
echo 【二】设置python环境变量
setx PATH "D:\caika\python37;D:\caika\python37\Scripts;%PATH%;" /m
echo.
echo 【三】将mysql设置为系统服务
D:\caika\mysql-8.0.31\bin\mysqld --install
echo.
echo 【四】启动mysql
net start mysql
echo.
echo 【五】将启动脚本复制到桌面
set d=%USERPROFILE%\Desktop
copy D:\caika\rpa\*.lnk %d%
echo.
echo 财咖网银助手安装完成,  请点击桌面caika图标启动系统!
@pause