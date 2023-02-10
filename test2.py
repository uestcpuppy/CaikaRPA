import time
import os
import utils

from selenium import webdriver

cmd = 'tasklist /v /fi "IMAGENAME eq iexplore.exe"'
titles = ["中国建设银行 企业网上银行"]
cpid = "0"

def killBrowser():
    with os.popen(cmd, 'r') as f:
        text = f.read()
        f.close()
        s = text.split("\n")
        for i in range(3,len(s)):
            for title in titles:
                #if 包含标题 && PID <> 当前浏览器的PID 就关闭
                pid = s[i][25:35].strip()
                if cpid != pid and s[i].find(title) != -1:
                    print ("killed pop browser PID is:"+pid)
                    return utils.stopTask(pid)

while True:
    killBrowser()
    time.sleep(0.5)
