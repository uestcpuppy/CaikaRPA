@echo off
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c pushd ""%~dp0"" && ""%~s0"" ::","","runas",1)(window.close)&&exit
echo 设置python环境变量
setx PATH "D:\caika\python37;D:\caika\python37\Scripts;%PATH%;" /m
echo 将mysql设置为系统服务
D:\caika\mysql-8.0.31\bin\mysqld --install
echo 启动mysql
net start mysql
echo 将启动脚本复制到桌面
set d=%USERPROFILE%\Desktop
copy D:\caika\rpa\caika.bat %d%
echo 财咖网银助手安装完成,  请点击桌面caika图标启动系统!
@pause