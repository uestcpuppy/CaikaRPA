import pymysql
import pandas as pd
import datetime
import utils
import openpyxl
import config
import os

def getDb():
    config={
        "host":"localhost",
        "user":"root",
        "password":"caika2020",
        "database":"caika_goski",
        "cursorclass": pymysql.cursors.DictCursor
    }
    db = pymysql.connect(**config)
    return db

def getQueryResultAll(sql):
    # print (sql)
    db = getDb()
    cursor = db.cursor()
    cursor.execute(sql)
    res = cursor.fetchall() #第一次执行
    cursor.close()
    db.close()
    return res

def query(sql):
    # 1. 创建数据库连接对象
    result = True
    con = getDb()
    try:
        # 2. 通过连接对象获取游标
        with con.cursor() as cursor:
            cursor.execute(sql)
        # 4. 操作成功提交事务
        con.commit()
        return result
    except Exception as e:
        print (e)
        con.rollback()
        return False
    finally:
        # 5. 关闭连接释放资源
        con.close()


def getQueryResultOne(sql):
    res = getQueryResultAll(sql)
    if len(res) == 1:
        return res[0]
    else:
        return None

def getSlotList():
    sql = "SELECT s.*, e.status, e.balance, c.name as company_name, e.query_begin_date,e.query_end_date,e.xls_filename,e.screenshot_filename,a.short_name,b.`name` FROM slot as s " \
          "LEFT JOIN execution as e ON s.execution_id = e.id " \
          "LEFT JOIN account as a ON s.account_id = a.id " \
          "LEFT JOIN company as c ON a.company_id = c.id " \
          "LEFT JOIN bank as b ON a.bank_id = b.id order by slot_num asc"
    # print (sql)
    res = getQueryResultAll(sql)
    return res

def getSlotInfo(slotNum):
    sql = "SELECT s.*,a.*,e.balance,e.status, e.query_begin_date,e.query_end_date,e.xls_filename,e.screenshot_filename,b.`name`,b.short_name as bank FROM slot as s " \
          "LEFT JOIN execution as e ON s.execution_id = e.id " \
          "LEFT JOIN account as a ON s.account_id = a.id " \
          "LEFT JOIN bank as b ON a.bank_id = b.id where s.slot_num="+slotNum
    res = getQueryResultOne(sql)
    return res

def updateExecution(executionId, status="",runEndDatetime="",xlsFilename="",imgFilename="", balance=""):
    sql = "UPDATE execution SET id = id"
    if status!="":
        sql = sql + ",status = '"+status+"'"
    if runEndDatetime!="":
        sql = sql + ",run_end_datetime= '"+runEndDatetime+"'"
    if xlsFilename!="":
        sql = sql + ",xls_filename = '"+xlsFilename+"'"
    if imgFilename!="":
        sql = sql + ",screenshot_filename = '"+imgFilename+"'"
    if balance!="":
        sql = sql + ",balance = '"+balance+"'"
    sql = sql + " WHERE id = "+executionId
    return query(sql)

def createCompany(name):
    # 1. 创建数据库连接对象
    con = getDb()
    # 2. 通过连接对象获取游标
    with con.cursor() as cursor:
            try:
                # 3. 通过游标执行SQL并获得执行结果
                sql = "INSERT INTO `company` VALUES (NULL,'%s')"%(name)
                result = cursor.execute(sql)
                # 4. 操作成功提交事务
                con.commit()
            except Exception as e:
                con.rollback()
                return False
    # 5. 关闭连接释放资源
    con.close()
    return True

def updateCompany(id, name):
    sql = "UPDATE company SET name = '"+name+"' where id = "+id
    return query(sql)

def removeCompany(companyId):
    sql = "delete from company where id = "+companyId
    return query(sql)

def createSlot(slotNum, accountId):
    # 1. 创建数据库连接对象
    con = getDb()
    # 2. 通过连接对象获取游标
    with con.cursor() as cursor:
            try:
                # 3. 通过游标执行SQL并获得执行结果
                sql = "INSERT INTO `slot` VALUES ('%s','%s', 0, 0)"%(slotNum, accountId)
                result = cursor.execute(sql)
                # 4. 操作成功提交事务
                con.commit()
            except Exception as e:
                con.rollback()
                return False
    # 5. 关闭连接释放资源
    con.close()
    return True

def removeSlot(slotNum):
    sql = "delete from slot where slot_num = "+slotNum
    return query(sql)

def createTemplate(templateName,bankId,sheetName, skipFirstRows, skipLastRows,transactionTime,income,expense,balance,customerAccountName,customerAccountNum,customerBankName,transactionId,summary,timeFormat,order,field1,field2,field3):
    # 1. 创建数据库连接对象
    con = getDb()
    # 2. 通过连接对象获取游标
    with con.cursor() as cursor:
            try:
                # 3. 通过游标执行SQL并获得执行结果
                sql = "INSERT INTO `template` VALUES (NULL, '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(templateName,
                                                                                                                                      bankId,
                                                                                                                                      sheetName,
                                                                                                                                      skipFirstRows,
                                                                                                                                      skipLastRows,
                                                                                                                                      transactionTime,
                                                                                                                                      income,
                                                                                                                                      expense,
                                                                                                                                      balance,
                                                                                                                                      customerAccountName,
                                                                                                                                      customerAccountNum,
                                                                                                                                      customerBankName,
                                                                                                                                      transactionId,
                                                                                                                                      summary,
                                                                                                                                      timeFormat,
                                                                                                                                      order,
                                                                                                                                      field1,
                                                                                                                                      field2,
                                                                                                                                      field3)
                result = cursor.execute(sql)
                # 4. 操作成功提交事务
                con.commit()
            except Exception as e:
                con.rollback()
                return False
    # 5. 关闭连接释放资源
    con.close()
    return True


def updateTemplate(id,templateName,bankId,sheetName,skipFirstRows,skipLastRows,transactionTime,income,expense,balance,customerAccountName,customerAccountNum,customerBankName,transactionId,summary,timeFormat,order,field1,field2,field3):
    sql = "UPDATE template SET name = '"+templateName+"'"
    sql = sql + ",bank_id = '"+bankId+"'"
    sql = sql + ",sheet_name= '"+sheetName+"'"
    sql = sql + ",skip_firstrows = '"+skipFirstRows+"'"
    sql = sql + ",skip_lastrows = '"+skipLastRows+"'"
    sql = sql + ",transaction_time = '" + transactionTime + "'"
    sql = sql + ",income = '" + income + "'"
    sql = sql + ",expense = '" + expense + "'"
    sql = sql + ",balance = '" + balance + "'"
    sql = sql + ",customer_account_name = '" + customerAccountName + "'"
    sql = sql + ",customer_account_num = '" + customerAccountNum + "'"
    sql = sql + ",customer_bank_name = '" + customerBankName + "'"
    sql = sql + ",transaction_id = '" + transactionId + "'"
    sql = sql + ",summary = '" + summary + "'"
    sql = sql + ",time_format = '" + timeFormat + "'"
    sql = sql + ",template.order = '" + order + "'"
    sql = sql + ",field_1 = '" + field1 + "'"
    sql = sql + ",field_2 = '" + field2 + "'"
    sql = sql + ",field_3 = '" + field3 + "'"
    sql = sql + " WHERE id = "+id
    return query(sql)

def removeTemplate(id):
    sql = "delete from template where id = "+id
    return query(sql)

def getTemplateList():
    sql = "SELECT t.*, b.`name` as bank_name FROM template as t, bank as b where t.bank_id = b.id order by id asc"
    return getQueryResultAll(sql)

def createAccount(companyId, shortName, accountNum, loginAccount, loginPwd, confirmPwd, bankId, templateId):
    # 1. 创建数据库连接对象
    con = getDb()
    # 2. 通过连接对象获取游标
    with con.cursor() as cursor:
            try:
                # 3. 通过游标执行SQL并获得执行结果
                sql = "INSERT INTO `account` VALUES (NULL,'%s','%s','%s','%s','%s','%s','%s','%s',NULL)"%(accountNum, shortName,loginAccount, loginPwd,confirmPwd, companyId,bankId,templateId)
                result = cursor.execute(sql)
                # 4. 操作成功提交事务
                con.commit()
            except Exception as e:
                con.rollback()
                return False
    # 5. 关闭连接释放资源
    con.close()
    return True

def updateAccount(id, loginAccount, companyId, shortName ,accountNum, loginPwd, confirmPwd, bankId, templateId):
    sql = "UPDATE account SET short_name = '"+shortName+"'"
    sql = sql + ",account_num = '"+accountNum+"'"
    sql = sql + ",login_pwd = '"+loginPwd+"'"
    sql = sql + ",confirm_pwd = '"+confirmPwd+"'"
    sql = sql + ",bank_id = '" + bankId + "'"
    sql = sql + ",template_id = '" + templateId + "'"
    sql = sql + ",company_id = '" + companyId + "'"
    sql = sql + ",login_account = '" + loginAccount + "'"
    sql = sql + " WHERE id = "+id
    return query(sql)

def removeAccount(id):
    sql = "delete from account where id = "+id
    return query(sql)

def getBankList():
    sql = "select * from bank order by id asc"
    return getQueryResultAll(sql)

def createExecution(slotNum,accountId,queryBeginDate,queryEndDate,isBill,isBalance,isAck):
    runBeginDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO `execution` VALUES (NULL,%s,%s,'%s','%s','READY','%s',NULL,'','',NULL,%s,%s,%s)"%(slotNum,accountId,queryBeginDate,queryEndDate,runBeginDatetime,isBill,isBalance,isAck)
    res = False
    # 1. 向execution中插入一条数据 2.更新slot的execution_id
    con = getDb()
    try:
        # 2. 通过连接对象获取游标
        with con.cursor() as cursor:
            result = cursor.execute(sql)
            if result != 1:
                raise Exception("DB操作出错")
            else:
                insertId = con.insert_id()
                pid = utils.runTask(str(insertId), slotNum, queryBeginDate, queryEndDate)
                # pid = 123456
                if type(pid) == int and pid>0:
                    sql2 = "UPDATE slot SET execution_id = " + str(insertId) + ",pid=" + str(pid) + " where slot_num = " + slotNum
                    result2 = cursor.execute(sql2)
                    res = (result2==1)
                else:
                    raise Exception("创建任务失败!")
        # 3. 操作成功提交事务
        con.commit()
        return res
    except Exception as e:
        print (e)
        con.rollback()
        return res
    finally:
        # 5. 关闭连接释放资源
        con.close()

def getExecution(executionId):
    sql = "SELECT e.*, a.short_name as account_name, a.account_num from execution as e, account as a where e.account_id = a.id and e.id = "+executionId
    return getQueryResultOne(sql)

def getExecutionList(accountId):
    sql = "SELECT e.*,e.id as execution_id, a.short_name as account_name,b.name as bank_name  from execution as e " \
          "LEFT JOIN account as a on e.account_id = a.id " \
          "LEFT JOIN bank as b on a.bank_id = b.id " \
          "where e.account_id = "+accountId+" order by e.id desc"
    return getQueryResultAll(sql)

def getAccountInfo(accountId):
    sql = "SELECT * from account as a,template as t where a.template_id = t.id and a.id = "+accountId
    return getQueryResultOne(sql)

def getAccountList(companyId):
    sql = "select a.*,c.name as company_name from account as a,company as c where a.company_id = c.id and a.company_id = "+ companyId
    if(companyId == "0"):
        sql = "select a.*,c.name as company_name from account as a,company as c where a.company_id = c.id order by a.company_id"
    res = getQueryResultAll(sql)
    return res

def getDetailListForExport(accountIds, beginDate, endDate):
    sql = "select d.*,a.short_name,a.account_num,c.`name` as company_name from detail as d " \
          "LEFT JOIN account as a ON d.account_id = a.id " \
          "LEFT JOIN company as c ON a.company_id = c.id " \
          "where  d.account_id in ("+accountIds+") and " \
          "d.transaction_time between '"+beginDate+" 00:00:00' and '"+endDate+" 23:59:59' order by d.account_id"
    res = getQueryResultAll(sql)
    return res

def getDetailListCount(accountId, beginDate, endDate, filter="all"):
    #filter = income, expense, all
    condition = ""
    if filter == "income":
        condition = "and income>0"
    elif filter == "expense":
        condition = "and expense>0"
    elif filter == "all":
        condition = ""
    sql = "select count(*) as count from detail where account_id = '"+ accountId+"' and transaction_time between '"+beginDate+" 00:00:00' and '"+endDate+" 23:59:59' "+condition+" order by id "
    res = getQueryResultAll(sql)
    return {"count":res[0]["count"]}

def getDetailList(accountId, beginDate, endDate, pageNum=1, pageSize=10000, filter="all"):
    #filter = income, expense, all
    condition = ""
    if filter == "income":
        condition = "and income>0"
    elif filter == "expense":
        condition = "and expense>0"
    elif filter == "all":
        condition = ""
    offset = (pageNum-1)*pageSize
    sql = "select * from detail where account_id = '"+ accountId+"' and transaction_time between '"+beginDate+" 00:00:00' and '"+endDate+" 23:59:59' "+condition+" order by DATE_FORMAT( `transaction_time`, '%Y-%m-%d'), id limit "+str(offset)+","+str(pageSize)
    res = getQueryResultAll(sql)
    return res

def getAccountListAll():
    # sql = "SELECT a.id,a.short_name,a.account_num,c.`name` as company_name from account as a,company as c where a.company_id = c.id order by a.company_id"
    sql = "SELECT a.*,t.`name` as template_name, b.`name` as bank_name,c.`name` as company_name,CAST(FROM_BASE64(login_pwd) as CHAR(100)) as login_pwd_new,CAST(FROM_BASE64(a.confirm_pwd) as CHAR(100)) as confirm_pwd_new from account as a " \
          "LEFT JOIN company as c ON a.company_id = c.id " \
          "LEFT JOIN bank as b on b.id = a.bank_id " \
          "LEFT JOIN template as t ON t.id = a.template_id " \
          "order by id asc"
    res = getQueryResultAll(sql)
    return res

def getCompanyAccountInfo(companyId, beginDate, endDate):
    accountList = getAccountList(companyId)
    result = []
    for account in accountList:
        #期初余额, 期末余额, 累计支出, 累计收入
        accountResult = account
        accountResult["first_balance"] = 0
        accountResult["last_balance"] = 0
        detailList = getDetailList(str(account["id"]), beginDate, endDate)
        if len(detailList) > 0:
            accountResult["first_balance"] = detailList[0]["balance"] - detailList[0]["income"] + detailList[0]["expense"]
            accountResult["last_balance"] = detailList[-1]["balance"]
        total_income = 0
        total_expense = 0
        for detail in detailList:
            total_income = total_income + detail["income"]
            total_expense = total_expense + detail["expense"]
        accountResult["total_income"] = total_income
        accountResult["total_expense"] = total_expense
        result.append(accountResult)
    return result

def createDetailList(detailList):
    # 1. 创建数据库连接对象
    con = getDb()
    try:
        # 2. 通过连接对象获取游标
        with con.cursor() as cursor:
            for detailDict in detailList:
                # 3. 通过游标执行SQL并获得执行结果
                sql = "INSERT INTO `detail` VALUES (NULL,%s,'%s',%s,%s,%s,'%s','%s','%s','%s','%s')"%(detailDict["account_id"],
                                                                                          detailDict["transaction_time"],
                                                                                          detailDict["income"],
                                                                                          detailDict["expense"],
                                                                                          detailDict["balance"],
                                                                                          detailDict["customer_account_name"],
                                                                                          detailDict["customer_account_num"],
                                                                                          detailDict["customer_bank_name"],
                                                                                          detailDict["transaction_id"],
                                                                                          detailDict["summary"])
                result = cursor.execute(sql)
                # if not (result == 1):
                #     raise Exception("插入detail出错")
        # 4. 操作成功提交事务
        con.commit()
        return True, str(len(detailList))
    except Exception as e:
        con.rollback()
        return False, str(e)
    finally:
        # 5. 关闭连接释放资源
        con.close()

def createUniqueDetailList(detailList):
    # 1. 创建数据库连接对象
    con = getDb()

    affectCount = 0

    with con.cursor() as cursor:
        try:
            for detailDict in detailList:
                # 3. 通过游标执行SQL并获得执行结果
                # detail表创建了UNIQUE索引防止数据重复, 插入的时候入遇到重复数据会自动忽略, 没有重复数据才会插入
                sql = "INSERT IGNORE INTO `detail` VALUES (NULL,%s,'%s',%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s')"%(detailDict["account_id"],
                                                                                      detailDict["transaction_time"],
                                                                                      detailDict["income"],
                                                                                      detailDict["expense"],
                                                                                      detailDict["balance"],
                                                                                      detailDict["customer_account_name"],
                                                                                      detailDict["customer_account_num"],
                                                                                      detailDict["customer_bank_name"],
                                                                                      detailDict["transaction_id"],
                                                                                      detailDict["summary"],
                                                                                      detailDict["field1"],
                                                                                      detailDict["field2"],
                                                                                      detailDict["field3"])
                cursor.execute(sql)
                affectCount = affectCount + con.affected_rows()
            # 4. 操作成功提交事务
            con.commit()
        except Exception as e:
            print(str(e))
            con.rollback()
            return False, str(e)
        finally:
            con.close()
        return True, str(affectCount)

def exportDetailXls(detailList):
    wb = openpyxl.load_workbook("template.xlsx")
    sheet1 = wb['导出信息']
    lastAccountNum = ""
    for i in detailList:
        income = ""
        expense = ""
        accountNum = ""
        companyName = ""
        bankShortName = ""
        if i["income"] >0:
            income = i["income"]
        if i["expense"] >0:
            expense = i["expense"]
        if lastAccountNum != i["account_num"]:
            accountNum = i["account_num"]
            bankShortName = i["short_name"]
            companyName = i["company_name"]
            lastAccountNum = accountNum
        #解决导入ERP日期报错的Bug
        date = datetime.datetime.strptime(str(i["transaction_time"])[0:10], '%Y-%m-%d')
        sheet1.append([companyName,"",accountNum,bankShortName,"","", date.date(),"",i["summary"],i["customer_account_name"],i["customer_account_num"], income,expense])
    filePath = config.DOWNLOAD_TEMP_DIR + "data.xlsx"
    if os.path.exists(filePath):
        os.remove(filePath)
    wb.save(config.DOWNLOAD_TEMP_DIR + "data.xlsx")
    return os.path.exists(filePath)

def importBankXls(account_id, filePath):

    accountInfo = getAccountInfo(account_id)

    df = pd.read_excel(filePath, accountInfo["sheet_name"], accountInfo["skip_firstrows"], keep_default_na=False)

    # 行索引
    newInexValues = df.index.values[0:len(df.index.values)-accountInfo["skip_lastrows"]]
    #如果是xls中的数据是降序, 反转list,确保导入是先发生先导入
    if accountInfo["order"] == 1:
        newInexValues = reversed(newInexValues)

    #  行数 （不包含表头，且一下均如此）
    # print(len(newInexValues))
    detailList = []
    for i in newInexValues:
        rowData = df.loc[i].to_list()
        detailDict = {}
        detailDict["account_id"] = account_id

        dtList = accountInfo["transaction_time"].split(',')
        dtStr = ""
        for i in dtList:
            dtStr = dtStr + str(rowData[int(i)-1]) + " "
        dtStr = dtStr.strip()

        # rawDateTime = rowData[accountInfo["transaction_time"]-1]
        rawDateTime = dtStr

        dt = datetime.datetime.strptime(rawDateTime, accountInfo["time_format"])
        detailDict["transaction_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        #如果income,expense,balance是字符串, 转换为浮点数
        if isinstance(rowData[accountInfo["income"]-1], str):
            if rowData[accountInfo["income"]-1].strip() == "":
                rowData[accountInfo["income"] - 1] = 0
            else:
                rowData[accountInfo["income"]-1] = float(rowData[accountInfo["income"] - 1].strip().replace(",", "").replace("-","0"))
        if isinstance(rowData[accountInfo["expense"]-1], str):
            if rowData[accountInfo["expense"]-1].strip() == "":
                rowData[accountInfo["expense"] - 1] = 0
            else:
                rowData[accountInfo["expense"]-1] = float(rowData[accountInfo["expense"] - 1].strip().replace(",", "").replace("-","0"))
        if isinstance(rowData[accountInfo["balance"]-1], str):
            rowData[accountInfo["balance"] - 1] = float(rowData[accountInfo["balance"] - 1].replace(",", ""))

        if(rowData[accountInfo["income"]-1] > 0):
            detailDict["income"] = rowData[accountInfo["income"] - 1]
        else:
            detailDict["income"] = 0

        if(detailDict["income"] == 0):
            detailDict["expense"] = abs(rowData[accountInfo["expense"] - 1])
        else:
            detailDict["expense"] = 0

        detailDict["balance"] = rowData[accountInfo["balance"] - 1]
        detailDict["customer_account_name"] = rowData[accountInfo["customer_account_name"]-1]
        detailDict["customer_account_num"] = rowData[accountInfo["customer_account_num"]-1]

        if(accountInfo["customer_bank_name"] == 0):
            detailDict["customer_bank_name"] = ""
        else:
            detailDict["customer_bank_name"] = rowData[accountInfo["customer_bank_name"] - 1]

        #中国银行需要特殊处理
        if(accountInfo["name"] == "中国银行模板"):
            #如果交易金额大于零, 那么对方账号去付款方账号
            if(rowData[14 - 1] > 0):
                detailDict["customer_account_name"] = rowData[6 - 1]
                detailDict["customer_account_num"] = rowData[5 - 1]
                detailDict["customer_bank_name"] = rowData[4 - 1]
            else:
                detailDict["customer_account_name"] = rowData[10 - 1]
                detailDict["customer_account_num"] = rowData[9 - 1]
                detailDict["customer_bank_name"] = rowData[8 - 1]

        if(accountInfo["transaction_id"] == 0):
            detailDict["transaction_id"] = ""
        else:
            detailDict["transaction_id"] = rowData[accountInfo["transaction_id"] - 1]

        if(accountInfo["summary"] == 0):
            detailDict["summary"] = ""
        else:
            detailDict["summary"] = rowData[accountInfo["summary"] - 1]

        if(accountInfo["field_1"] == 0):
            detailDict["field1"] = ""
        else:
            detailDict["field1"] = rowData[accountInfo["field_1"] - 1]

        if(accountInfo["field_2"] == 0):
            detailDict["field2"] = ""
        else:
            detailDict["field2"] = rowData[accountInfo["field_2"] - 1]

        if(accountInfo["field_3"] == 0):
            detailDict["field3"] = ""
        else:
            detailDict["field3"] = rowData[accountInfo["field_3"] - 1]

        # detailDict["transaction_id"] = rowData[accountInfo["transaction_id"]-1]
        # detailDict["summary"] = rowData[accountInfo["summary"]-1]
        detailList.append(detailDict)
    return createUniqueDetailList(detailList)


if __name__ == '__main__':
    # importBankXls("105", "D:\\caika\\BOB_1202.xlsx")
    pass