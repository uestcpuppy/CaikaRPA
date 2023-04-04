import time
from win32com import client

ACCOUNT_CN_DICT = {}
ACCOUNT_CN_DICT[1] = "9558059000410193"
ACCOUNT_CN_DICT[2] = "GSB00029025918"
ACCOUNT_CN_DICT[3] = "BJRCBE8113341941"
ACCOUNT_CN_DICT[4] = "BJRCBE8314328993"
ACCOUNT_CN_DICT[5] = "B06423120"
ACCOUNT_CN_DICT[6] = "GSB00005248325"
ACCOUNT_CN_DICT[7] = "GSB00010312511"
ACCOUNT_CN_DICT[8] = "GSB00010312510"
ACCOUNT_CN_DICT[9] = "GSB00024427371"
ACCOUNT_CN_DICT[10] = "GSB00029025452"
ACCOUNT_CN_DICT[11] = "GSB00024427391"
ACCOUNT_CN_DICT[12] = "GSB00024427275"
ACCOUNT_CN_DICT[13] = "GSB00029025337"
ACCOUNT_CN_DICT[14] = "9558059001383983"
ACCOUNT_CN_DICT[15] = "9558059000410031"
ACCOUNT_CN_DICT[16] = "9558059003250716"
ACCOUNT_CN_DICT[17] = "9558059003250763"
ACCOUNT_CN_DICT[18] = "9558059001570878"
ACCOUNT_CN_DICT[19] = "9558059000408750"
ACCOUNT_CN_DICT[20] = "9558059001377823"
ACCOUNT_CN_DICT[21] = "9558059001383955"
ACCOUNT_CN_DICT[23] = "9558059000395601"
ACCOUNT_CN_DICT[24] = "9558059000204935"
ACCOUNT_CN_DICT[25] = "9558059001377892"
ACCOUNT_CN_DICT[26] = "9558059002320410"

def getUKeyList(bankname):
    classid = ""
    func = ""
    if bankname == "PSBC":
        # C:\Program Files (x86)\PSBC PowerAssist\PowerSignPSBC.dll
        classid = "{F3E92562-1B4D-4BFA-B2D4-E9BCABE3C505}"
        func = "getCertList"
        pass
    elif bankname == "CCB":
        # C:\Program Files (x86)\CCBComponents\Detector\CCB_GMSignCom.dll
        classid = "{7F432EA4-52B9-442C-AFBD-E1A73AD87043}"
        func = "getCertCN"
        pass
    elif bankname == "BJRCB":
        # C:\Program Files (x86)\BJRCB PowerAssist\PowerSignBJRCB.dll
        classid = "{2F4EE3C0-7E30-4EE8-91FD-6688CC4ADC79}"
        func = "getCertList"
        pass
    else:
        return ""
    control = client.Dispatch(classid)
    keylist = eval("control."+func+"()")
    return keylist

def getUKeyLoad(bankname, certcommonname, retrytimes, interval):
    while retrytimes > 0:
        certlist = getUKeyList(bankname)
        print(certcommonname)
        if certlist.find(certcommonname) != -1:
            return True
        retrytimes = retrytimes - 1
        time.sleep(interval)
    return False


# print(getUKeyList("PSBC"))
#output CN=9558059000410193,1186393643;

# print(getUKeyList("CCB"))
#output GSB0002902591
#三个的其中一个

# print(getUKeyList("BJRBC"))
#output CN=BJRCBE8113341941,1279782999;  序列号+证书ID

# print (getUKeyLoad("PSBC", ACCOUNT_CN_DICT[1], 10, 1))

