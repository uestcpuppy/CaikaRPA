#!/usr/bin/python
import time
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import parse_qsl, parse_qs
import json
import utils
import config
from usb.usbhub import usbhub
import database
import datetime
import shutil
import re
from io import BytesIO
import os

LOG_PATH = config.PROJECT_ROOT + "rpa.log"

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

        else:
            return json.JSONEncoder.default(self, obj)

class myHandler(BaseHTTPRequestHandler):

    def responseJsonData(self, data, withDateEncoder=False):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if not withDateEncoder:
            return self.wfile.write(json.dumps(data).encode())
        else:
            return self.wfile.write(json.dumps(data,cls=DateEncoder).encode())

    def getQueryStrParam(self, key):
        qs_dict = parse_qs(self.path[1:], keep_blank_values=True)
        return qs_dict[key][0]

    def dowload(self, realPath, mimetype):
        realPath = realPath.replace("/", "\\")
        f = open(realPath, "rb")
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    def do_GET(self):

        if self.path.find("createTemplate") !=-1:
            templateName = self.getQueryStrParam("templateName")
            bankId = self.getQueryStrParam("bankId")
            sheetName = self.getQueryStrParam("sheetName")
            skipFirstRows = self.getQueryStrParam("skipFirstRows")
            skipLastRows = self.getQueryStrParam("skipLastRows")
            trasactionTime = self.getQueryStrParam("trasactionTime")
            income = self.getQueryStrParam("income")
            expense = self.getQueryStrParam("expense")
            balance = self.getQueryStrParam("balance")
            customerAccountName = self.getQueryStrParam("customerAccountName")
            customerAccountNum = self.getQueryStrParam("customerAccountNum")
            customerBankName = self.getQueryStrParam("customerBankName")
            transactionId = self.getQueryStrParam("transactionId")
            summary = self.getQueryStrParam("summary")
            timeFormat = self.getQueryStrParam("timeFormat")
            result = database.createTemplate(templateName,
                                             bankId,
                                             sheetName,
                                             skipFirstRows,
                                             skipLastRows,
                                             trasactionTime,
                                             income,
                                             expense,
                                             balance,
                                             customerAccountName,
                                             customerAccountNum,
                                             customerBankName,
                                             transactionId,
                                             summary,
                                             timeFormat)
            self.responseJsonData({"result":result})

        if self.path.find("updateCompany") !=-1:
            id = self.getQueryStrParam("id")
            name = self.getQueryStrParam("name")
            result = database.updateCompany(id, name)
            self.responseJsonData({"result":result})

        if self.path.find("updateAccount") !=-1:
            id = self.getQueryStrParam("id")
            loginAccount = self.getQueryStrParam("loginAccount")
            companyId = self.getQueryStrParam("companyId")
            shortName = self.getQueryStrParam("shortName")
            accountNum = self.getQueryStrParam("accountNum")
            loginPwd = self.getQueryStrParam("loginPwd")
            confirmPwd = self.getQueryStrParam("confirmPwd")
            bankId = self.getQueryStrParam("bankId")
            templateId = self.getQueryStrParam("templateId")
            result = database.updateAccount(id, loginAccount, companyId, shortName, accountNum, loginPwd, confirmPwd, bankId, templateId)
            self.responseJsonData({"result":result})

        if self.path.find("createAccount") !=-1:
            companyId = self.getQueryStrParam("companyId")
            shortName = self.getQueryStrParam("shortName")
            accountNum = self.getQueryStrParam("accountNum")
            loginAccount = self.getQueryStrParam("loginAccount")
            loginPwd = self.getQueryStrParam("loginPwd")
            confirmPwd = self.getQueryStrParam("confirmPwd")
            bankId = self.getQueryStrParam("bankId")
            templateId = self.getQueryStrParam("templateId")
            result = database.createAccount(companyId, shortName, accountNum, loginAccount, loginPwd, confirmPwd, bankId, templateId)
            self.responseJsonData({"result":result})

        if self.path.find("getBankList") !=-1:
            result = database.getBankList()
            self.responseJsonData(result)

        if self.path.find("createSlot") !=-1:
            slotNum = self.getQueryStrParam("slotNum")
            accountId = self.getQueryStrParam("accountId")
            result = database.createSlot(slotNum, accountId)
            self.responseJsonData({"result":result})

        if self.path.find("createCompany") !=-1:
            name = self.getQueryStrParam("name")
            result = database.createCompany(name)
            self.responseJsonData({"result":result})

        if self.path.find("removeCompany") !=-1:
            companyId = self.getQueryStrParam("companyId")
            result = database.removeCompany(companyId)
            self.responseJsonData({"result":result})

        if self.path.find("removeAccount") !=-1:
            id = self.getQueryStrParam("id")
            result = database.removeAccount(id)
            self.responseJsonData({"result":result})

        if self.path.find("removeTemplate") !=-1:
            id = self.getQueryStrParam("id")
            result = database.removeTemplate(id)
            self.responseJsonData({"result":result})

        if self.path.find("removeSlot") !=-1:
            slotNum = self.getQueryStrParam("slotNum")
            result = database.removeSlot(slotNum)
            self.responseJsonData({"result":result})

        if self.path.find("stopTask") !=-1:
            slotNum = self.getQueryStrParam("slotNum")
            slotInfo = database.getSlotInfo(slotNum)
            executionId = slotInfo["execution_id"]
            pid = slotInfo["pid"]
            utils.stopTask(pid)
            result = database.updateExecution(str(executionId), status="FAILED", runEndDatetime=utils.getNowTime())
            self.responseJsonData({"result":result})

        if self.path.find("getExecutionList") !=-1:
            accountId = self.getQueryStrParam("accountId")
            result = database.getExecutionList(accountId)
            self.responseJsonData(result,True)

        if self.path.find("importBankXls") !=-1:
            executionIds = self.getQueryStrParam("executionIds")
            executionIdList  = executionIds.split(",")
            res = []
            for executionId in executionIdList:
                execution = database.getExecution(executionId)
                xlsFilePath = config.DOWNLOAD_DIR + executionId + "\\"+execution["xls_filename"]
                result, msg = database.importBankXls(str(execution["account_id"]), xlsFilePath)
                res.append({"result":result, "account_name": execution["account_name"], "msg": msg})
            self.responseJsonData(res)

        if self.path.find("download") !=-1:
            filePath = config.DOWNLOAD_DIR + self.path[10:]
            self.dowload(filePath, "application/octet-stream")

        if self.path.find("getCompanyList") !=-1:
            result = database.getQueryResultAll("SELECT * FROM company")
            self.responseJsonData(result)

        if self.path.find("getTemplateList") !=-1:
            result = database.getQueryResultAll("SELECT t.*, b.`name` as bank_name FROM template as t, bank as b where t.bank_id = b.id order by id asc")
            self.responseJsonData(result)

        if self.path.find("getDetailExport") !=-1:
            accountIds = self.getQueryStrParam("AccountIds")
            beginDate = self.getQueryStrParam("BeginDate")
            endDate = self.getQueryStrParam("EndDate")
            detailList = database.getDetailListForExport(accountIds, beginDate, endDate)
            result = database.exportDetailXls(detailList)
            self.dowload(config.DOWNLOAD_TEMP_DIR+"data.xlsx", "application/octet-stream")
            # self.responseJsonData(result)

        if self.path.find("getAllAccountList") !=-1:
            result = database.getAccountListAll()
            self.responseJsonData(result)

        if self.path.find("getAccountList") !=-1:
            companyId = self.getQueryStrParam("CompanyId")
            result = database.getQueryResultAll("SELECT * FROM account where company_id="+companyId)
            self.responseJsonData(result)

        if self.path.find("getDetailCount") !=-1:
            accountId = self.getQueryStrParam("AccountId")
            beginDate = self.getQueryStrParam("BeginDate")
            endDate = self.getQueryStrParam("EndDate")
            filter = self.getQueryStrParam("filter")
            result = database.getDetailListCount(accountId, beginDate, endDate, filter)
            self.responseJsonData(result)

        if self.path.find("getDetailList") !=-1:
            pageNum = self.getQueryStrParam("PageNum")
            accountId = self.getQueryStrParam("AccountId")
            beginDate = self.getQueryStrParam("BeginDate")
            endDate = self.getQueryStrParam("EndDate")
            pageSize = self.getQueryStrParam("PageSize")
            filter = self.getQueryStrParam("filter")
            result = database.getDetailList(accountId, beginDate, endDate, int(pageNum), int(pageSize), filter)
            self.responseJsonData(result, True)
            return

        if self.path.find("getCompanyAccountInfo") !=-1:
            companyId = self.getQueryStrParam("CompanyId")
            beginDate = self.getQueryStrParam("BeginDate")
            endDate = self.getQueryStrParam("EndDate")
            result = database.getCompanyAccountInfo(companyId, beginDate, endDate)
            self.responseJsonData(result)

        if self.path.find("setDeviceStatus") !=-1:
            slotNum = self.getQueryStrParam("SlotNum")
            result = {}
            usb = usbhub()
            result["result"] = usb.switchSlot(int(slotNum), 1)
            # result["result"] = usb.setDeviceStatus(int(slotNum))
            self.responseJsonData(result)

        if self.path.find("getUsbHubStatus") !=-1:
            usb = usbhub()
            result = {}
            result["result"] = usb.isUsbHubWorking()
            self.responseJsonData(result)

        if self.path.find("getUsbStatus") !=-1:
            usb = usbhub()
            result = usb.getDeviceStatus()
            self.responseJsonData(result)

        if self.path.find("getLastLog") !=-1:
            #获取最后1000条日志
            result = utils.getLastLog(LOG_PATH)
            self.responseJsonData(result)

        if self.path.find("getSlotList") !=-1:
            result = database.getSlotList()
            self.responseJsonData(result,True)

        if self.path.find("getSlotInfo") !=-1:
            slotNum = self.getQueryStrParam("slotNum")
            result = database.getSlotInfo(slotNum)
            self.responseJsonData(result,True)

        if self.path.find("getTask") !=-1:
            slotNum = self.getQueryStrParam("SlotNum")
            data = utils.getTask(slotNum)
            result = {"SlotNum": slotNum,
                       "BatchId": data["BatchId"],
                       "Status": data["Status"],
                       "BillDownloadFile":utils.getBillDownloadFile(slotNum, data["BatchId"]),
                       "PhotoDownloadFile":utils.getPhotoDownloadFile(slotNum, data["BatchId"])}
            self.responseJsonData(result)

        if self.path.find("runTask") !=-1:
            slotNum = self.getQueryStrParam("slotNum")
            queryBeginDate = self.getQueryStrParam("beginDate")
            queryEndDate = self.getQueryStrParam("endDate")
            accounInfo = database.getSlotInfo(slotNum)
            result = database.createExecution(slotNum,accounInfo["account_id"],queryBeginDate,queryEndDate)
            self.responseJsonData({"result":result})

        if self.path=="/":

            self.path="/index.html"

        try:

            #Check the file extension required and

            #set the right mime type

            sendReply = False

            if self.path.endswith(".html"):

                mimetype='text/html'

                sendReply = True

            if self.path.endswith(".jpg"):

                mimetype='image/jpg'

                sendReply = True

            if self.path.endswith(".gif"):

                mimetype='image/gif'

                sendReply = True

            if self.path.endswith(".png"):

                mimetype='image/png'

                sendReply = True

            if self.path.endswith(".js"):

                mimetype='application/javascript'

                sendReply = True

            if self.path.endswith(".css"):

                mimetype='text/css'

                sendReply = True

            # if self.path.endswith(".png"):
            #
            #     mimetype = 'application/png'
            #     self.dowload(self.path, mimetype)
            #     return

            if sendReply == True:

                #Open the static file requested and send it
                realPath = config.PROJECT_ROOT + "web" + self.path
                realPath = realPath.replace("/", "\\")
                f = open(realPath, "rb")
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()

            return

        except IOError:

            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):

        if self.path.find("uploadFile") !=-1:
            accountId = self.getQueryStrParam("AccountId")
            """Serve a POST request."""
            r, info = self.deal_post_data()
            print(r, info, "by: ", self.client_address)
            f = BytesIO()
            f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
            f.write(b"<html>\n<title>Upload Result Page</title>\n")
            if r:
                try:
                    result, msg = database.importBankXls(accountId, info)
                except Exception as e:
                    result = False
                    msg = str(e)
                if result:
                    f.write(("<strong>导入成功"+msg+"条记录</strong>").encode('utf-8'))
                else:
                    f.write(("<strong>导入失败:"+msg+"</strong>").encode('utf-8'))
            else:
                f.write("<strong>导入失败</strong>".encode('utf-8'))
            # f.write(info.encode('utf-8'))
            f.write(b"</body>\n</html>\n")
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html;charset=utf-8")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            if f:
                shutil.copyfileobj(f, self.wfile)
                f.close()

    def deal_post_data(self):
        boundary = self.headers["Content-Type"].split("=")[1].encode('utf-8')
        remain_bytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remain_bytes -= len(line)
        if boundary not in line:
            return False, "Content NOT begin with boundary"
        line = self.rfile.readline()
        remain_bytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode('utf-8'))
        if not fn:
            return False, "Can't find out file name..."
        # path = translate_path(self.path)
        path = config.UPLOAD_PATH
        fn = os.path.join(path, fn[0])
        #如果文件名不是.xls, .xlsx 提示失败
        if fn.find(".xls") == -1:
            return False, "  请导入正确的文件类型(xls或xlsx)"
        while os.path.exists(fn):
            fn += "_"
        line = self.rfile.readline()
        remain_bytes -= len(line)
        line = self.rfile.readline()
        remain_bytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return False, "Can't create file to write, do you have permission to write?"

        pre_line = self.rfile.readline()
        remain_bytes -= len(pre_line)
        while remain_bytes > 0:
            line = self.rfile.readline()
            remain_bytes -= len(line)
            if boundary in line:
                pre_line = pre_line[0:-1]
                if pre_line.endswith(b'\r'):
                    pre_line = pre_line[0:-1]
                out.write(pre_line)
                out.close()
                return True, "%s" % fn
            else:
                out.write(pre_line)
                pre_line = line
        return False, "Unexpect Ends of data."

try:

    #Create a web server and define the handler to manage the

    #incoming request

    server = HTTPServer(('', config.PORT_NUMBER_WEB), myHandler)

    print ('Started httpserver on port ' , config.PORT_NUMBER_WEB)

    #Wait forever for incoming htto requests

    server.serve_forever()

except KeyboardInterrupt:


    server.socket.close()