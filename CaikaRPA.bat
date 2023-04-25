%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c pushd ""%~dp0"" && ""%~s0"" ::","","runas",1)(window.close)&&exit
cd D:\caika\rpa
python -u WebServer.py >> D:\caika\rpa\web.log 2>&1
@pause