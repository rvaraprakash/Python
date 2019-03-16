import numpy as np

import pandas as pd
from datetime import datetime
import re
import xlrd
from openpyxl import Workbook
from os import listdir
import xlsxwriter
from os.path import isfile, join
import os

confFile="C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\BHN_CHG\Vara.txt"
#confFile="Vara.txt"

OUTPUT_FILE = "ChargeFileValidation.xlsx" ### Default value

try:
    fh = open(confFile)
    lines = [line for line in fh.readlines() if line.strip('\n')]
    fh.close()
except FileNotFoundError:
    print(confFile, ": File Not found, please check and try again")
    exit (-1)

#### Read Configuration file
for curline in lines:
    if curline.startswith('#'):
        pass
       # print("Its comment line:" + curline)
    else:
        #print("config line:" + curline)
        res = curline.split('=')
        if (res[0].strip() == 'BL_RATED'):
            BL_RATED_filename = res[1].strip('\n')
            BL_RATED_filename = BL_RATED_filename.strip('"')
            BL_RATED_filename = BL_RATED_filename.strip()
            print("BL_RATED_filename:",BL_RATED_filename,":")
            if os.path.exists(BL_RATED_filename) != True:
                print("File not exists:'",BL_RATED_filename,"'")
                exit(-1)
        elif (res[0].strip() == 'CHARGE_FILES_PATH'):
            CHARGE_FILES_PATH = res[1].strip('\n')
            CHARGE_FILES_PATH = CHARGE_FILES_PATH.strip()
            CHARGE_FILES_PATH = CHARGE_FILES_PATH.strip('"')
            if os.path.exists(CHARGE_FILES_PATH) != True:
                print("File not exists:", CHARGE_FILES_PATH)
                exit(-1)
        elif (res[0].strip() == 'BILLING_SYS_INFO'):
            BillingInfoFile = res[1].strip('\n')
            BillingInfoFile = BillingInfoFile.strip()
            BillingInfoFile = BillingInfoFile.strip('"')
            if os.path.exists(BillingInfoFile) != True:
                print("File not exists:", BillingInfoFile)
                exit(-1)
        elif (res[0].strip() == 'OUTPUT_FILE'):
            OUTPUT_FILE = res[1].strip('\n')
            OUTPUT_FILE = OUTPUT_FILE.strip()
            OUTPUT_FILE = OUTPUT_FILE.strip('"')
            if os.path.exists(OUTPUT_FILE) != True:
                print("File not exists:", OUTPUT_FILE)
                exit(-1)

#### Declare variables required for reading charge files
a_chargeFilesList = list()
a_chargeFilesRecDict = {}
a_chargeFilesRecCntDict = {}
a_chargeFilesRecSpltDict = {}

a_BHN_df = pd.DataFrame(columns=['FileName','AccountNum','ChargeNumber','Amount','CallType','Service'])
a_CSG_df = pd.DataFrame(columns=['FileName','AccountNum','ChargeNumber','Amount','CallType','AccType'])
a_ICOMS_df = pd.DataFrame(columns=['FileName','CreditDebitInd','AccountNum','ChargeNumber','Amount'])
a_NATIONAL_df = pd.DataFrame(columns=['FileName','CreditDebitInd','DivisionCode','AccountNum','ChargeNumber','Amount'])
a_NYC_df = pd.DataFrame(columns=['FileName','Division','AccountNum','ChargeNumber','DialedDigit',
                                 'CallType','Account_Flag','ServiceCode','Amount'])


#### Division code
PRI_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
RES_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
BCP_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
TRKSM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'NYC', 'LNK', 'LXM', 'CTX', 'HWI']
PRISM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'LNK', 'LXM', 'CTX', 'HWI']
PRIMDEV_DIV = ['NYC']

###Key fields
CHRG_KEYS = ['BILLER','FINANCE_ENTITY','ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'SERVICE_TYPE','ACCOUNT_TYPE', 'AR_ROUNDED_PRICE', 'CALL_TYPE',
             'CALL_COMP_CALL_TYPE','CREDIT_DEBIT_IND','CHG_FILENAME']
ACC_SERV_KEYS = ['ACCOUNT_TYPE', 'SERVICE_TYPE']
ICOMS_KEYS = ['FINANCE_ENTITY', 'CREDIT_DEBIT_IND','ACCOUNT_NUMBER','CHARGE_NUMBER','ACCOUNT_TYPE', 'SERVICE_TYPE', 'CALL_TYPE', 'CALL_COMP_CALL_TYPE',
              'TAX_INCLUSIVE_IND','AR_ROUNDED_PRICE','USAGE_CYCLE_END']
RES_DF_FILTER_KEYS = ['BILLER', 'FINANCE_ENTITY','ACCOUNT_NUMBER','CHARGE_NUMBER','SERVICE_TYPE','ACCOUNT_TYPE','CALL_TYPE','CALL_COMP_CALL_TYPE',
                 'CREDIT_DEBIT_IND','AR_ROUNDED_PRICE','CHG_FILENAME']

### If charge file specified
try:
    if CHARGE_FILES_PATH is not None:
        a_chargeFilesList = [f for f in listdir(CHARGE_FILES_PATH) if isfile(join(CHARGE_FILES_PATH, f))]
        for file in a_chargeFilesList:
            if file[-3:] == 'job':
                a_chargeFilesList.remove(file)
        print("CHARGE_FILES",a_chargeFilesList)
except NameError:
    print("CHARGE_FILES_PATH not defined")


#### Functions to read content of charge files
def addToMap(file):
    print("Reading file:", file)
    if file[-3:] == 'job':
        print("Skipping file:", file)
    else:
        fh = open(file)
        lines = [line for line in fh.readlines() if line.strip('\n')]
        fh.close()
        lst = list()
        for line in lines:
            line.strip('\n')
            lst.append(line)
        key = os.path.basename(file)
        a_chargeFilesRecDict[key] = lst

def parseRecords_BHN(file):
    key = os.path.basename(file)
    recs = a_chargeFilesRecDict[key]
    global a_BHN_df
    l_accNum = list()
    l_chgrNum = list()
    l_amount = list()
    l_callType = list()
    l_service = list()
    l_fileName = list()
    for rec in recs:
        #print(rec)
        if re.findall(r"^H", rec):
            #print("Header:" + rec)
            l_header = rec.split(',')[0]
            l_hdrRecCount = rec.split(',')[1]
            #print(a_BHN_df)
        elif re.findall(r"^F", rec):
            #print("Footer:" + rec)
            l_footer = rec.split(',')[0]
            l_ftrRecCount = rec.split(',')[1]
        else:
            #print("Actual Record:" + rec)
            l_accNum.append(rec[0:16])
            l_chgrNum.append(rec[16:26])
            l_amount.append(rec[26:33])
            l_callType.append(rec[33:35])
            l_service.append(rec[35:36])
            l_fileName.append(key)
    ### From Dict
    bhn_dict = {'FileName': l_fileName,
                'AccountNum':l_accNum,
                'ChargeNumber': l_chgrNum,
                'Amount': l_amount,
                'CallType': l_callType,
                'Service':l_service}

    tmp_df = pd.DataFrame.from_dict(bhn_dict)
    a_BHN_df = pd.concat([a_BHN_df, tmp_df], sort=True)
    #print("a_BHN_df:", a_BHN_df)

def parseRecords_ICOMS(file):
    key = os.path.basename(file)
    recs = a_chargeFilesRecDict[key]
    global a_ICOMS_df
    l_cdInd = list()
    l_accNum = list()
    l_chgrNum = list()
    l_amount = list()
    l_fileName = list()
    for rec in recs:
        #print(rec)
        if re.findall(r"^H", rec):
            #print("Header:" + rec)
            l_header = rec.split(',')[0]
            l_hdrTotAmount = rec.split(',')[1]
        elif re.findall(r"^F", rec):
            #print("Footer:" + rec)
            l_footer = rec.split(',')[0]
            l_ftrTotAmount = rec.split(',')[1]
        else:
            #print("Actual Record:" + rec)
            l_cdInd.append(rec.split(',')[0][:1])
            l_accNum.append(rec.split(',')[0][1:])
            l_chgrNum.append(rec.split(',')[1])
            l_amount.append(rec.split(',')[2])
            l_fileName.append(key)
    ### From Dict
    icoms_dict = {'FileName': l_fileName,
                'CreditDebitInd': l_cdInd,
                'AccountNum':l_accNum,
                'ChargeNumber': l_chgrNum,
                'Amount': l_amount}

    #print("icoms_dict:",icoms_dict)
    tmp1_df = pd.DataFrame.from_dict(icoms_dict)
    a_ICOMS_df = pd.concat([a_ICOMS_df, tmp1_df], sort=False)
    #print("a_ICOMS_df:", a_ICOMS_df)
    print("a_ICOMS_df.AccountNum:", a_ICOMS_df['AccountNum'])


def parseRecords_NATIONAL(file):
    key = os.path.basename(file)
    recs = a_chargeFilesRecDict[key]
    global a_NATIONAL_df
    l_cdInd = list()
    l_divCode = list()
    l_accNum = list()
    l_chgrNum = list()
    l_amount = list()
    l_fileName = list()
    for rec in recs:
        #print(rec)
        if re.findall(r"^H", rec):
            #print("Header:" + rec)
            l_header = rec.split(',')[0]
            l_hdrTotAmount = rec.split(',')[1]
        elif re.findall(r"^F", rec):
            #print("Footer:" + rec)
            l_footer = rec.split(',')[0]
            l_ftrTotAmount = rec.split(',')[1]
        else:
            #print("Actual Record:" + rec)
            l_cdInd.append(rec.split(',')[0][:1])
            l_divCode.append(rec.split(',')[0][1:])
            l_accNum.append(rec.split(',')[1])
            l_chgrNum.append(rec.split(',')[2])
            l_amount.append(rec.split(',')[3])
            l_fileName.append(key)
    ### From Dict
    national_dict = {'FileName': l_fileName,
                'CreditDebitInd': l_cdInd,
                'DivisionCode': l_divCode,
                'AccountNum':l_accNum,
                'ChargeNumber': l_chgrNum,
                'Amount': l_amount}

    #print("icoms_dict:",national_dict)
    tmp_df = pd.DataFrame.from_dict(national_dict)
    a_NATIONAL_df = pd.concat([a_NATIONAL_df, tmp_df], sort=False)
    #print("a_NATIONAL_df:", a_NATIONAL_df)
    print("a_NATIONAL_df.AccountNum:", a_NATIONAL_df['AccountNum'])

def parseRecords_CSG(file):
    key = os.path.basename(file)
    recs = a_chargeFilesRecDict[key]
    global a_CSG_df
    l_accNum = list()
    l_chgrNum = list()
    l_amount = list()
    l_callType = list()
    l_accType = list()
    l_fileName = list()
    for rec in recs:
        #print(rec)
        if re.findall(r"^H", rec):
            #print("Header:" + rec)
            l_header = rec.split(',')[0]
            l_hdrRecCount = rec.split(',')[1]
            #print(a_BHN_df)
        elif re.findall(r"^F", rec):
            #print("Footer:" + rec)
            l_footer = rec.split(',')[0]
            l_ftrRecCount = rec.split(',')[1]
        else:
            #print("Actual Record:" + rec)
            l_accNum.append(rec[0:16])
            l_chgrNum.append(rec[16:26])
            l_amount.append(rec[26:33])
            l_callType.append(rec[33:39])
            l_accType.append(rec[39:40])
            l_fileName.append(key)
    ### From Dict
    csg_dict = {'FileName': l_fileName,
                'AccountNum':l_accNum,
                'ChargeNumber': l_chgrNum,
                'Amount': l_amount,
                'CallType': l_callType,
                'AccType':l_accType}

    tmp_df = pd.DataFrame.from_dict(csg_dict)
    a_CSG_df = pd.concat([a_CSG_df, tmp_df], sort=False)
    #print("a_CSG_df:", a_CSG_df)

def parseRecords_NYC(file):
    key = os.path.basename(file)
    if (key.split('.')[1] == 'job'):
        return
    recs = a_chargeFilesRecDict[key]
    global a_NYC_df
    l_accNum = list()
    l_chgrNum = list()
    l_dialDigit = list()
    l_resComFlag = list()
    l_servCode = list()
    l_amount = list()
    l_callType = list()
    l_division = list()
    l_fileName = list()
    l_callDuration = list()
    for rec in recs:
        rec = rec.strip('\n')
        #print("rec:",rec,":")
        if len(rec) == 2:
            #print("Header:" + rec)
            l_header = rec
        else:
            #print("Actual Record:" + rec)
            l_division.append(rec.split(',')[1])
            l_accNum.append(rec.split(',')[4])
            l_chgrNum.append(rec.split(',')[5])
            l_dialDigit.append(rec.split(',')[28])
            l_callType.append(rec.split(',')[94])
            l_resComFlag.append(rec.split(',')[97])
            l_servCode.append(rec.split(',')[99])
            l_amount.append(rec.split(',')[123])
            l_fileName.append(key)
    ### From Dict
    nyc_dict = {'FileName': l_fileName,
                'Division': l_division,
                'AccountNum':l_accNum,
                'ChargeNumber': l_chgrNum,
                'DialedDigit':l_dialDigit,
                'CallType': l_callType,
                'Account_Flag': l_resComFlag,
                'ServiceCode': l_servCode,
                'Amount': l_amount}

    tmp_df = pd.DataFrame.from_dict(nyc_dict)
    a_NYC_df = pd.concat([a_NYC_df, tmp_df], sort=False)
    #print("a_NYC_df:", a_NYC_df)

def parseFile_BHN(file):
    #print ("Parsing BHN file:" + file)
    addToMap(file)
    parseRecords_BHN(file)
    #print(a_BHN_df)
    key = os.path.basename(file)
    ### Remove one header and trailer count
    recCount = int(str(len(a_chargeFilesRecDict[key]) - 2))
    key = key[:11] + "xxxx.txt"
    #print(key + ":" + recCount)
    a_chargeFilesRecCntDict[key]=recCount

def parseFile_ICOMS(file):
    print ("Parsing ICOMS file:" + file)
    addToMap(file)
    parseRecords_ICOMS(file)
    key = os.path.basename(file)
    ### Remove one header and trailer count
    recCount = int(str(len(a_chargeFilesRecDict[key]) - 2))
    #print(key + ":" + recCount)
    a_chargeFilesRecCntDict[key] = recCount

def parseFile_NATIONAL(file):
    print ("Parsing NATIONAL file:" + file)
    addToMap(file)
    parseRecords_NATIONAL(file)
    key = os.path.basename(file)
    ### Remove one header and trailer count
    recCount = int(str(len(a_chargeFilesRecDict[key]) - 2))
    #print(key + ":" + recCount)
    a_chargeFilesRecCntDict[key] = recCount

def parseFile_CSG(file):
    #print ("Parsing CSG file:" + file)
    addToMap(file)
    parseRecords_CSG(file)
    key = os.path.basename(file)
    recCount = int(str(len(a_chargeFilesRecDict[key])))
    #print(key + ":" + recCount)
    a_chargeFilesRecCntDict[key] = recCount

def parseFile_NYC(file):
    #print ("Parsing NYC file:" + file)
    addToMap(file)
    parseRecords_NYC(file)
    key = os.path.basename(file)
    ### Remove one header count
    recCount = int(str(len(a_chargeFilesRecDict[key]) - 1 ))
    #print(key + ":" + recCount)
    a_chargeFilesRecCntDict[key] = recCount

for file in a_chargeFilesList:
    if (re.search(r"^RES|^BUS", file)):
        #print ("BHN file:" + file)
        file=CHARGE_FILES_PATH + "/" + file
        parseFile_BHN(file)
    elif (re.search(r"\.BCP|RES[a-z,A-Z]|\.PRI", file)):
        #print ("ICOMS file:" + file)
        file=CHARGE_FILES_PATH + "/" + file
        parseFile_ICOMS(file)
    elif (re.search(r"NSBCP|NSPRIP", file)):
        #print ("NATIONAL file:" + file)
        file=CHARGE_FILES_PATH + "/" + file
        parseFile_NATIONAL(file)
    elif (re.search(r"^twcvp", file)):
        #print ("CSG file:" + file)
        file=CHARGE_FILES_PATH + "/" + file
        parseFile_CSG(file)
    elif (re.search(r"^twnyc", file)):
        #print ("NYC file:" + file)
        file=CHARGE_FILES_PATH + "/" + file
        parseFile_NYC(file)
    else:
        print("INVALID FILE:" + file)

if a_chargeFilesRecCntDict:
    a_recCount_df = pd.DataFrame(list(a_chargeFilesRecCntDict.items()), columns=['ChargeFileName','Actual_Count'])
#print(a_recCount_df)

### Build Data frame for BL_RATED

fileType = os.path.basename(BL_RATED_filename).split('.')[1]
#print("fileType:" + fileType)
if (fileType == "csv"):
    df = pd.read_csv(BL_RATED_filename)
else:
    df = pd.read_excel(BL_RATED_filename)

### Load Reference table data
BI_DF = pd.read_excel(BillingInfoFile, sheet_name='Information')
#print("BI_DF:", BI_DF)

BHN_Ref_DF = pd.read_excel(BillingInfoFile, sheet_name='BHN_REF')

clean_df = df[df['AR_ROUNDED_PRICE'] > 0]
clean_df.ACCOUNT_NUMBER = clean_df.ACCOUNT_NUMBER.astype(np.int64)



#### build ICOMS charge filename
def createFile_ICOMS(row):
    filename = row['FINANCE_ENTITY'] + row['fileTime']
    if (row['CREDIT_DEBIT_IND'] == 'D'):
        filename = filename + "0000"
    else:
        filename = filename + "0001"

    if (row['SERVICE_TYPE'] == 'R'):
        filename = filename + ".RESP"
    elif (row['SERVICE_TYPE'] == 'B') or (row['SERVICE_TYPE'] == 'F'):
        filename = filename + ".BCPP"
    elif (row['SERVICE_TYPE'] == 'T'):
        filename = filename + ".PRIP"
    #print("Tax Ind:", row['TAX_INCLUSIVE_IND'])
    if (row['TAX_INCLUSIVE_IND'] == 0):
        filename = filename + "taxed"
    else:
        filename = filename + "untaxed"
    filenum=""
    print("Call type: ",row['CALL_TYPE'])
    if re.findall(r"DA|CC|OA[1-6]", row['CALL_TYPE']):
        filenum=1
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        filenum=2
    if re.findall(r"LOCT1|LD1", row['CALL_TYPE']):
        filenum=3
    if re.findall(r"LOCT2|LD2|LD3|LD7", row['CALL_TYPE']):
        filenum=4
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        filenum=5
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC1|LOCT1|LD1", row['CALL_COMP_CALL_TYPE']):
        filenum=6
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC2|LOCT2|LD2|LD3|LD7", row['CALL_COMP_CALL_TYPE']):
        filenum=7
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LD4", row['CALL_COMP_CALL_TYPE']):
        filenum=8
    filename += str(filenum) + ".txt"
    #print (" ----")
    #print(filename)
    return filename


#### build NS charge filename
def createFile_NS(row):
    filename = row['fileTime']
    if (row['CREDIT_DEBIT_IND'] == 'D'):
        filename = filename + "0000"
    else:
        filename = filename + "0001"

    if (row['SERVICE_TYPE'] == 'R'):
        filename = filename + ".RESP"
    elif (row['SERVICE_TYPE'] == 'B') or (row['SERVICE_TYPE'] == 'F'):
        filename = filename + ".NSBCP"
    elif (row['SERVICE_TYPE'] == 'T'):
        filename = filename + ".NSPRIP"
    #print("Tax Ind:", row['TAX_INCLUSIVE_IND'])
    if (row['TAX_INCLUSIVE_IND'] == 0):
        filename = filename + "taxed"
    else:
        filename = filename + "untaxed"
    filenum=""
    #print("Call type: ",row['CALL_TYPE'])
    if re.findall(r"DA|CC|OA[1-6]", row['CALL_TYPE']):
        filenum=1
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        filenum=2
    if re.findall(r"LOCT1|LD1", row['CALL_TYPE']):
        filenum=3
    if re.findall(r"LOCT2|LD2|LD3|LD7", row['CALL_TYPE']):
        filenum=4
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        filenum=5
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC1|LOCT1|LD1", row['CALL_COMP_CALL_TYPE']):
        filenum=6
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC2|LOCT2|LD2|LD3|LD7", row['CALL_COMP_CALL_TYPE']):
        filenum=7
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LD4", row['CALL_COMP_CALL_TYPE']):
        filenum=8
    filename += str(filenum) + ".txt"
    #print(filename)
    return filename

#### build CSG charge filename
def createFile_CSG(row):
    filename = "twcvp.bu0."
    region = BI_DF[BI_DF['Finance Entity'] == row['FINANCE_ENTITY']]['Region ID'].tolist()[0]
    filename =  filename + str(region) + "v01"
    if (row['SERVICE_TYPE'] == 'T'):
        filename = filename + ".trksum"
    elif (row['SERVICE_TYPE'] == 'B') or (row['SERVICE_TYPE'] == 'F') or (row['SERVICE_TYPE'] == 'R'):
        filename = filename + ".primsum"

    filename = filename + "." + row['fileTime']
    filename += "001.dat"
    return filename

#### build CSG charge filename
def createFile_CSG_NYC(row):
    filename = "twnyc1p.bu0.primalv00.rated."
    filename = filename + row['fileTime']
    filename += "001.dat"
    return filename


#### build BHN charge filename
def createFile_BHN(row):
    filename = ""
    if (row['SERVICE_TYPE'] == 'R'):
        filename = filename + "RES"
    elif (row['SERVICE_TYPE'] == 'B') or (row['SERVICE_TYPE'] == 'T'):
        filename = filename + "BUS"

    filename = filename + row['fileTime']
    filename += "xxxx.txt"
    return filename

### BHN Call Type mapping
def getCallType_BHN(row):
    #callType = row['CALL_TYPE']
    #CD_id = row['CREDIT_DEBIT_IND']
    #ccType = row['CALL_COMP_CALL_TYPE']
    #print("callType:", callType)
    #print("CD_id:", CD_id)
    #print("ccType:", ccType)
    res_df = BHN_Ref_DF[(BHN_Ref_DF['CallType'] == row['CALL_TYPE']) &
                        (BHN_Ref_DF['CreditDebitInd'] == row['CREDIT_DEBIT_IND'])]
   # print("Row:", row[['ACCOUNT_NUMBER','CALL_TYPE','CREDIT_DEBIT_IND']])
    #res_df.reset_index()
    if (len(res_df) > 1):
        #print("res_df:", res_df['CallCompCallType'])
        #print("row:", ccType)
        tmp_df = res_df[res_df['CallCompCallType'].str.contains(row['CALL_COMP_CALL_TYPE']) & ~res_df['CallCompCallType'].str.contains('<>')]
        #print("tmp_df:", tmp_df)
        if (len(tmp_df) == 0):
            tmp_df = res_df[~res_df['CallCompCallType'].str.contains(row['CALL_COMP_CALL_TYPE']) & res_df[
                'CallCompCallType'].str.contains('<>')]
        return str(int(tmp_df['ChargFile_callType'])).zfill(2)
    else:
        #print("Row 1...:", row[['ACCOUNT_NUMBER','CALL_TYPE','CREDIT_DEBIT_IND']])
        return str(int(res_df['ChargFile_callType'])).zfill(2)

### CSG Call Type mapping
def getCallType_CSG(row):
    print("CSG Call type:",row['CALL_TYPE'])
    if row['CALL_TYPE'] in ['LOCT1','LD1']:
        return "INTRA1"
    elif row['CALL_TYPE'] in ['LOCT2', 'LD2', 'LD3', 'LD7']:
        return "INTER1"
    elif (row['CALL_TYPE'] in ['LD4', 'LD5', 'LD6', 'INT']) | (row['CALL_TYPE'] in ['TERR']):
        return "INT001"
    elif (row['CALL_TYPE'] in ['OA1', 'OA2', 'OA3', 'OA4','OA5','OA6']) | (row['CALL_TYPE'] in ['OA[1-6]']):
        return "OS0001"
    elif row['CALL_TYPE'] in ['DA', 'CC']:
        return "DA0001"
    elif (row['CALL_TYPE'] in ['OA8']) & (row['CALL_COMP_CALL_TYPE'] in ['LOC1', 'LOCT1', 'LD1']):
        return "IN8001"
    elif (row['CALL_TYPE'] in ['OA8']) & (row['CALL_COMP_CALL_TYPE'] in ['LOC2','LOCT2','LD2','LD3','LD7']):
        return "IN8002"
    elif (row['CALL_TYPE'] in ['OA8']) & (row['CALL_COMP_CALL_TYPE'] in ['LD4']):
        return "IN8003"
    elif (row['CALL_TYPE'] in ['OA1', 'OA2', 'OA3', 'OA4','OA5','OA6']) & (row['CALL_COMP_CALL_TYPE'] in ['LD5', 'LD6', 'INT', 'TERR[1-99]']):
        return "OAINT1"
    elif (row['CALL_TYPE'] in ['DA', 'CC']) & (row['CREDIT_DEBIT_IND'] in ['C']):
        return "DACDOM"
    else:
        return "VARA"



### BHN Service Type mapping
def getServiceType_BHN(row):
    if row['SERVICE_TYPE'] == 'B':
        return row['ACCOUNT_TYPE']
    else:
        return row['SERVICE_TYPE']

### Compare results
def compareResults(row):
    if row['BILLER'] == 'BHN':
        if ((row['Amount']==row['Exp_AR_ROUNDED_PRICE']) &
            (row['Service']==row['Exp_SERVICE_TYPE'])):
            return "PASS"
        else:
            return "FAIL"
    if row['BILLER'] == 'CSG':
        if ((row['Amount']==row['Exp_AR_ROUNDED_PRICE']) &
            (row['CallType']==row['Exp_CALL_TYPE']) &
            (row['AccType'] == row['Exp_ACCOUNT_TYPE'])):
            return "PASS"
        else:
            return "FAIL"
    if row['BILLER'] == 'ICOMS':
        if ((row['Amount'] == row['Exp_AR_ROUNDED_PRICE']) &
            (row['CreditDebitInd'] == row['Exp_CREDIT_DEBIT_IND'])):
            return "PASS"
        else:
            return "FAIL"
    if row['BILLER'] == 'NATIONAL':
        if ((row['Amount'] == row['Exp_AR_ROUNDED_PRICE']) &
            (row['CreditDebitInd'] == row['Exp_CREDIT_DEBIT_IND'])):
            return "PASS"
        else:
            return "FAIL"
#### PRI Accounts
priAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(PRI_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'T'])
                     & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(priAcc_df)):
    #print("PRI Accounts")
    #print(priAcc_df[CHRG_KEYS])
    priAcc_df = priAcc_df.filter(ICOMS_KEYS)
    priAcc_df['fileTime'] = pd.to_datetime(priAcc_df['USAGE_CYCLE_END'])
    priAcc_df['fileTime'] = priAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    priAcc_df['CHG_FILENAME']= priAcc_df.apply(createFile_ICOMS, axis=1)
    priAcc_df.drop(['fileTime'], axis=1, inplace=True)
    priAcc_df['BILLER'] = "ICOMS"
    #print(priAcc_df)


#### RES Accounts
resAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(RES_DIV) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                     & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(resAcc_df)):
    print("RES Accounts")
    resAcc_df = resAcc_df.filter(ICOMS_KEYS)
    resAcc_df['fileTime'] = pd.to_datetime(resAcc_df['USAGE_CYCLE_END'])
    resAcc_df['fileTime'] = resAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    resAcc_df['CHG_FILENAME']= resAcc_df.apply(createFile_ICOMS, axis=1)
    resAcc_df.drop(['fileTime'], axis=1, inplace=True)
    resAcc_df['BILLER'] = "ICOMS"
    #print(resAcc_df)

#### BCP Accounts
bcpAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(BCP_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'F'])
                     & clean_df['SERVICE_TYPE'].isin(['B', 'F'])]
if (len(bcpAcc_df)):
    print("BCP Accounts")
    bcpAcc_df = bcpAcc_df.filter(ICOMS_KEYS)
    bcpAcc_df['fileTime'] = pd.to_datetime(bcpAcc_df['USAGE_CYCLE_END'])
    bcpAcc_df['fileTime'] = bcpAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    bcpAcc_df['CHG_FILENAME'] = bcpAcc_df.apply(createFile_ICOMS, axis=1)
    bcpAcc_df.drop(['fileTime'], axis=1, inplace=True)
    bcpAcc_df['BILLER'] = "ICOMS"
    #print(bcpAcc_df)


#### Trunksum_Accounts
trksumAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(TRKSM_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'T'])
                        & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(trksumAcc_df)):
    print("Trunksum_Accounts")
    trksumAcc_df = trksumAcc_df.filter(ICOMS_KEYS)
    trksumAcc_df['fileTime'] = pd.to_datetime(trksumAcc_df['USAGE_CYCLE_END'])
    trksumAcc_df['fileTime'] = trksumAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    trksumAcc_df['CHG_FILENAME'] = trksumAcc_df.apply(createFile_CSG, axis=1)
    trksumAcc_df.drop(['fileTime'], axis=1, inplace=True)
    trksumAcc_df['BILLER'] = "CSG"
    #print(trksumAcc_df)

#### Primsum_Accounts
primsumAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(TRKSM_DIV) & clean_df['ACCOUNT_TYPE'].isin(['R', 'C'])
                         & clean_df['SERVICE_TYPE'].isin(['B', 'F', 'R'])]
if (len(primsumAcc_df)):
    print("Primsum_Accounts")
    primsumAcc_df = primsumAcc_df.filter(ICOMS_KEYS)
    primsumAcc_df['fileTime'] = pd.to_datetime(primsumAcc_df['USAGE_CYCLE_END'])
    primsumAcc_df['fileTime'] = primsumAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    primsumAcc_df['CHG_FILENAME'] = primsumAcc_df.apply(createFile_CSG, axis=1)
    primsumAcc_df.drop(['fileTime'], axis=1, inplace=True)
    primsumAcc_df['BILLER'] = "CSG"
    #print(primsumAcc_df)

#### PrimdetNYC_Accounts
primdetAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['NYC']) & clean_df['ACCOUNT_TYPE'].isin(['R', 'C'])
                         & clean_df['SERVICE_TYPE'].isin(['B', 'F', 'R'])]
if (len(primdetAcc_df)):
    print("PrimdetNYC_Accounts")
    primdetAcc_df = primdetAcc_df.filter(ICOMS_KEYS)
    primdetAcc_df['fileTime'] = pd.to_datetime(primdetAcc_df['USAGE_CYCLE_END'])
    primdetAcc_df['fileTime'] = primdetAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    primdetAcc_df['CHG_FILENAME'] = primdetAcc_df.apply(createFile_CSG_NYC, axis=1)
    primdetAcc_df.drop(['fileTime'], axis=1, inplace=True)
    primdetAcc_df['BILLER'] = "CSG"
    #print(primdetAcc_df)

#### National_PRI_Accounts
npriAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(npriAcc_df)):
    #print("National_PRI_Accounts")
    npriAcc_df = npriAcc_df.filter(ICOMS_KEYS)
    npriAcc_df['fileTime'] = pd.to_datetime(npriAcc_df['USAGE_CYCLE_END'])
    npriAcc_df['fileTime'] = npriAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    npriAcc_df['CHG_FILENAME'] = npriAcc_df.apply(createFile_NS, axis=1)
    npriAcc_df.drop(['fileTime'], axis=1, inplace=True)
    npriAcc_df['BILLER'] = "NATIONAL"
    #print(npriAcc_df)

#### National_BCP_Accounts
nbcpAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['B', 'F'])]
if (len(nbcpAcc_df)):
    #print("National_BCP_Accounts")
    nbcpAcc_df = nbcpAcc_df.filter(ICOMS_KEYS)
    nbcpAcc_df['fileTime'] = pd.to_datetime(nbcpAcc_df['USAGE_CYCLE_END'])
    nbcpAcc_df['fileTime'] = nbcpAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    nbcpAcc_df['CHG_FILENAME'] = nbcpAcc_df.apply(createFile_NS, axis=1)
    nbcpAcc_df.drop(['fileTime'], axis=1, inplace=True)
    nbcpAcc_df['BILLER'] = "NATIONAL"
    #print(nbcpAcc_df)

#### BHN_RES_Accounts
bhnResAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                        & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(bhnResAcc_df)):
    #print("BHN_RES_Accounts")
    bhnResAcc_df = bhnResAcc_df.filter(ICOMS_KEYS)
    bhnResAcc_df['fileTime'] = pd.to_datetime(bhnResAcc_df['USAGE_CYCLE_END'])
    bhnResAcc_df['fileTime'] = bhnResAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    bhnResAcc_df['CHG_FILENAME'] = bhnResAcc_df.apply(createFile_BHN, axis=1)
    bhnResAcc_df.drop(['fileTime'], axis=1, inplace=True)
    bhnResAcc_df['BILLER'] = "BHN"
    #print(bhnResAcc_df)

#### BHN_COM_Accounts
bhnComAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['C','T'])
                        & clean_df['SERVICE_TYPE'].isin(['T', 'B'])]
if (len(bhnComAcc_df)):
    #print("BHN_COM_Accounts")
    bhnComAcc_df = bhnComAcc_df.filter(ICOMS_KEYS)
    bhnComAcc_df['fileTime'] = pd.to_datetime(bhnComAcc_df['USAGE_CYCLE_END'])
    bhnComAcc_df['fileTime'] = bhnComAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    bhnComAcc_df['CHG_FILENAME'] = bhnComAcc_df.apply(createFile_BHN, axis=1)
    bhnComAcc_df.drop(['fileTime'], axis=1, inplace=True)
    bhnComAcc_df['BILLER'] = "BHN"
    #print(bhnComAcc_df)

### Combine all DF's
frames = [priAcc_df, resAcc_df, bcpAcc_df, trksumAcc_df, primsumAcc_df, primdetAcc_df, npriAcc_df, nbcpAcc_df, bhnResAcc_df, bhnComAcc_df]
all_df=pd.DataFrame()

for frame in frames:
    if len(frame):
        all_df = pd.concat([all_df,frame])
all_df = all_df.sort_values(['CHG_FILENAME'])

charge_df = all_df.filter(CHRG_KEYS)
new_df = charge_df.groupby(['ACCOUNT_NUMBER', 'CHARGE_NUMBER'], as_index=False)['AR_ROUNDED_PRICE'].sum()
res_df = pd.merge(charge_df,new_df, on=['ACCOUNT_NUMBER','CHARGE_NUMBER'])
res_df.drop('AR_ROUNDED_PRICE_x', axis=1, inplace=True)
res_df.drop_duplicates(inplace=True)
res_df.rename(columns={'AR_ROUNDED_PRICE_y':'AR_ROUNDED_PRICE'}, inplace=True)
res_df = res_df[RES_DF_FILTER_KEYS]

filesCount_df = res_df.groupby(['BILLER','CHG_FILENAME']).count()['AR_ROUNDED_PRICE'].astype(int)
filesCount_df = filesCount_df.to_frame().reset_index()
filesCount_df.columns = ['BILLER','ChargeFileName', 'Exp_RecordsCount']

def summaryResult(row):
    if row['Exp_RecordsCount'] == row['Actual_Count']: return "PASS"
    else: return "FAIL"

if 'a_recCount_df' in locals():
    sum_result_df = pd.merge(filesCount_df,a_recCount_df, how='outer', on=['ChargeFileName'])
    #sum_result_df['Exp_RecordsCount'] = sum_result_df.Exp_RecordsCount.astype(str)

    #sum_result_df['Actual_Count'] = sum_result_df.Actual_Count.astype(int)
    sum_result_df['Result'] = sum_result_df.apply(summaryResult, axis=1)
else:
    sum_result_df = filesCount_df



try :
    writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
    sum_result_df.to_excel(writer,'RecCount Summary', index=False)

    ### Work on each biller
    billerList = res_df['BILLER'].unique()
    #print("biller List", billerList)
    for biller in billerList:
        print("Working on biller:",biller)
        if biller == 'BHN':
            print("Inside BHN..")
            BHN_df = pd.DataFrame()
            exp_bhn_RefCol = ['BILLER', 'ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'SERVICE_TYPE', 'ACCOUNT_TYPE', 'CALL_TYPE',
                              'CREDIT_DEBIT_IND', 'CALL_COMP_CALL_TYPE','AR_ROUNDED_PRICE']
            exp_bhn_df = res_df[res_df['BILLER'] == 'BHN']
            exp_bhn_df = exp_bhn_df.filter(exp_bhn_RefCol)
            exp_bhn_df['CALL_TYPE'] = exp_bhn_df.apply(getCallType_BHN, axis=1)
            exp_bhn_df['SERVICE_TYPE'] = exp_bhn_df.apply(getServiceType_BHN, axis=1)
            exp_bhn_df['AR_ROUNDED_PRICE'] = exp_bhn_df['AR_ROUNDED_PRICE']. \
                apply(lambda x: (str(format(x, '.2f')).split('.')[0] + str(format(x, '.2f')).split('.')[1]).zfill(7))
            exp_bhn_df.drop(['CREDIT_DEBIT_IND', 'ACCOUNT_TYPE'], axis=1, inplace=True)
            exp_bhn_df.rename(columns={'SERVICE_TYPE': 'Exp_SERVICE_TYPE',
                                       'CALL_TYPE': 'Exp_CALL_TYPE',
                                       'AR_ROUNDED_PRICE': 'Exp_AR_ROUNDED_PRICE'}, inplace=True)
            try:
                if a_BHN_df.empty != True:
                    a_BHN_df['AccountNum'] = a_BHN_df.AccountNum.astype(np.int64)
                    a_BHN_df['ChargeNumber'] = a_BHN_df.ChargeNumber.astype(np.int64)
                    a_BHN_df.rename(columns={'AccountNum': 'ACCOUNT_NUMBER',
                                             'ChargeNumber': 'CHARGE_NUMBER'}, inplace=True)


                    #BHN_df = pd.merge(a_BHN_df, exp_bhn_df, how='outer', on=['ACCOUNT_NUMBER', 'CHARGE_NUMBER'])
                    BHN_df = pd.merge(exp_bhn_df,a_BHN_df, how='outer', on=['ACCOUNT_NUMBER', 'CHARGE_NUMBER'])
                    BHN_df['Result'] = BHN_df.apply(compareResults, axis=1)
                    BHN_df = BHN_df[['BILLER','ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'Exp_AR_ROUNDED_PRICE','Amount',
                                     'Exp_CALL_TYPE','CallType','Exp_SERVICE_TYPE', 'Service', 'FileName','Result']]
                else:
                    BHN_df = exp_bhn_df
            except AttributeError:
                pass
            if (len(BHN_df) > 1):
                BHN_df.to_excel(writer, 'BHN', index=False)

        #### CSG
        if biller == 'CSG':
            print("Inside CSG..")
            CSG_df = pd.DataFrame()
            exp_csg_RefCol = ['BILLER', 'ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'ACCOUNT_TYPE', 'CALL_TYPE',
                              'CALL_COMP_CALL_TYPE', 'AR_ROUNDED_PRICE']
            exp_csg_df = res_df[res_df['BILLER'] == 'CSG']
            exp_csg_df = exp_csg_df.filter(exp_csg_RefCol)
            exp_csg_df['CALL_TYPE'] = exp_csg_df.apply(getCallType_CSG, axis=1)
            exp_csg_df['AR_ROUNDED_PRICE'] = exp_csg_df['AR_ROUNDED_PRICE'].\
               apply(lambda x: (str(format(x, '.2f')).split('.')[0]+str(format(x,'.2f')).split('.')[1]).zfill(7))
            exp_csg_df.rename(columns={'ACCOUNT_TYPE': 'Exp_ACCOUNT_TYPE',
                                       'CALL_TYPE': 'Exp_CALL_TYPE',
                                       'AR_ROUNDED_PRICE': 'Exp_AR_ROUNDED_PRICE'}, inplace=True)
            # exp_bhn_df.drop('CALL_TYPE',axis=1, inplace=True)

            try:
                if a_CSG_df.empty != True:
                    a_CSG_df['AccountNum'] = a_CSG_df.AccountNum.astype(np.int64)
                    a_CSG_df['ChargeNumber'] = a_CSG_df.ChargeNumber.astype(np.int64)
                    a_CSG_df.rename(columns={'AccountNum': 'ACCOUNT_NUMBER',
                                             'ChargeNumber': 'CHARGE_NUMBER'}, inplace=True)

                   # print("Colmn:", exp_csg_df.columns)
                    CSG_df = pd.merge(exp_csg_df,a_CSG_df, how='outer', on=['ACCOUNT_NUMBER', 'CHARGE_NUMBER'])
                    print("Colmn:", CSG_df.columns)
                    CSG_df['Result'] = CSG_df.apply(compareResults, axis=1)
                    CSG_df = CSG_df[['BILLER','ACCOUNT_NUMBER','CHARGE_NUMBER','Exp_ACCOUNT_TYPE','AccType',
                                     'Exp_CALL_TYPE','CallType','Exp_AR_ROUNDED_PRICE','Amount','CALL_COMP_CALL_TYPE',
                                     'FileName','Result']]
                else:
                    CSG_df = exp_csg_df
            except AttributeError:
                pass
            if (len(CSG_df) > 1):
                CSG_df.to_excel(writer, 'CSG', index=False)


        ### National
        if biller == 'NATIONAL':
            print("Inside NATIONAL..")
            NATIONAL_df = pd.DataFrame()
            exp_national_RefCol = ['BILLER', 'FINANCE_ENTITY','ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'CREDIT_DEBIT_IND', 'AR_ROUNDED_PRICE']
            exp_national_df = res_df[res_df['BILLER'] == 'NATIONAL']

            exp_national_df = exp_national_df.filter(exp_national_RefCol)

            exp_national_df['AR_ROUNDED_PRICE'] = exp_national_df['AR_ROUNDED_PRICE']. \
                apply(lambda x: (str(format(x, '.2f')).split('.')[0] + str(format(x, '.2f')).split('.')[1]))
            exp_national_df['AR_ROUNDED_PRICE'] = exp_national_df.AR_ROUNDED_PRICE.astype(np.int64)
            exp_national_df.rename(columns={'CREDIT_DEBIT_IND': 'Exp_CREDIT_DEBIT_IND',
                                            'FINANCE_ENTITY': 'Exp_DIVISION_CODE',
                                            'AR_ROUNDED_PRICE': 'Exp_AR_ROUNDED_PRICE'}, inplace=True)
            # exp_national_df.drop('CALL_TYPE',axis=1, inplace=True)

            try:
                if a_NATIONAL_df.empty != True:
                    print("National AccountNum:", a_NATIONAL_df['AccountNum'])
                    a_NATIONAL_df['AccountNum'] = a_NATIONAL_df.AccountNum.astype(np.int64)
                    a_NATIONAL_df['ChargeNumber'] = a_NATIONAL_df.ChargeNumber.astype(np.int64)
                    a_NATIONAL_df.rename(columns={'AccountNum': 'ACCOUNT_NUMBER',
                                               'ChargeNumber': 'CHARGE_NUMBER'}, inplace=True)

                    print("Amount:", a_NATIONAL_df['Amount'])
                    a_NATIONAL_df['Amount'] = a_NATIONAL_df.Amount.astype(np.int64)
                    print("Colmn:", a_NATIONAL_df.columns)
                    NATIONAL_df = pd.merge(exp_national_df, a_NATIONAL_df, how='outer', on=['ACCOUNT_NUMBER', 'CHARGE_NUMBER'])
                    NATIONAL_df['Result'] = NATIONAL_df.apply(compareResults, axis=1)
                    print("NATIONAL_df Colmn:", NATIONAL_df.columns)
                    NATIONAL_df = NATIONAL_df[['BILLER', 'ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'Exp_DIVISION_CODE', 'DivisionCode', 'Exp_CREDIT_DEBIT_IND', 'CreditDebitInd',
                         'Exp_AR_ROUNDED_PRICE', 'Amount', 'FileName', 'Result']]
                else:
                    NATIONAL_df = exp_national_df
            except AttributeError:
                pass
            if (len(NATIONAL_df) > 1):
                NATIONAL_df.to_excel(writer, 'NATIONAL', index=False)

        ### ICOMS
        if biller == 'ICOMS':
            print("Inside ICOMS..")
            ICOMS_df = pd.DataFrame()
            exp_icoms_RefCol = ['BILLER', 'ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'CREDIT_DEBIT_IND', 'AR_ROUNDED_PRICE']
            exp_icoms_df = res_df[res_df['BILLER'] == 'ICOMS']

            exp_icoms_df = exp_icoms_df.filter(exp_icoms_RefCol)

            exp_icoms_df['AR_ROUNDED_PRICE'] = exp_icoms_df['AR_ROUNDED_PRICE'].\
               apply(lambda x: (str(format(x, '.2f')).split('.')[0]+str(format(x,'.2f')).split('.')[1]))
            exp_icoms_df['AR_ROUNDED_PRICE'] = exp_icoms_df.AR_ROUNDED_PRICE.astype(np.int64)
            exp_icoms_df.rename(columns={'CREDIT_DEBIT_IND': 'Exp_CREDIT_DEBIT_IND',
                                       'AR_ROUNDED_PRICE': 'Exp_AR_ROUNDED_PRICE'}, inplace=True)
            # exp_bhn_df.drop('CALL_TYPE',axis=1, inplace=True)

            try:
                if a_ICOMS_df.empty != True:
                    print("ICOMS AccountNum:", a_ICOMS_df['AccountNum'])
                    a_ICOMS_df['AccountNum'] = a_ICOMS_df.AccountNum.astype(np.int64)
                    a_ICOMS_df['ChargeNumber'] = a_ICOMS_df.ChargeNumber.astype(np.int64)
                    a_ICOMS_df.rename(columns={'AccountNum': 'ACCOUNT_NUMBER',
                                             'ChargeNumber': 'CHARGE_NUMBER'}, inplace=True)

                    print("Amount:", a_ICOMS_df['Amount'])
                    a_ICOMS_df['Amount'] = a_ICOMS_df.Amount.astype(np.int64)
                    # print("Colmn:", exp_csg_df.columns)
                    ICOMS_df = pd.merge(exp_icoms_df, a_ICOMS_df, how='outer', on=['ACCOUNT_NUMBER', 'CHARGE_NUMBER'])
                    ICOMS_df['Result'] = ICOMS_df.apply(compareResults, axis=1)
                    ICOMS_df = ICOMS_df[['BILLER','ACCOUNT_NUMBER','CHARGE_NUMBER','Exp_CREDIT_DEBIT_IND','CreditDebitInd',
                                         'Exp_AR_ROUNDED_PRICE','Amount','FileName','Result']]
                else:
                    ICOMS_df = exp_icoms_df
            except AttributeError:
                pass
            if (len(ICOMS_df) > 1):
                ICOMS_df.to_excel(writer, 'ICOMS', index=False)

except PermissionError as e:
    print("\nERROR:", e)
    print("Please close file:'" + os.path.basename(OUTPUT_FILE) + "' and try again")
    exit(-1)

#except Exception as e:
 #   print("\nERROR:", e)


finally:
    all_df.to_excel(writer, 'All_Records', index=False)
    res_df.to_excel(writer, 'Aggr_Records', index=False)
    writer.save()

print("\nOutputfile:" + OUTPUT_FILE)
"""
#### BHN Data mapping
exp_bhn_df = pd.DataFrame()
BHN_df = pd.DataFrame()
if res_df.iloc[0]['BILLER'] == 'BHN':
    exp_bhn_RefCol = ['BILLER','ACCOUNT_NUMBER','CHARGE_NUMBER','SERVICE_TYPE','ACCOUNT_TYPE','CALL_TYPE',
                      'CREDIT_DEBIT_IND','AR_ROUNDED_PRICE']
    exp_bhn_df = res_df.filter(exp_bhn_RefCol)
    exp_bhn_df['CALL_TYPE'] = exp_bhn_df.apply(getCallType_BHN, axis=1)
    exp_bhn_df['SERVICE_TYPE'] = exp_bhn_df.apply(getServiceType_BHN, axis=1)
    exp_bhn_df['AR_ROUNDED_PRICE'] = exp_bhn_df['AR_ROUNDED_PRICE'].\
        apply(lambda x: (str(format(x, '.2f')).split('.')[0]+str(format(x,'.2f')).split('.')[1]).zfill(7))
    exp_bhn_df.drop(['CREDIT_DEBIT_IND','ACCOUNT_TYPE'], axis=1, inplace=True)
    exp_bhn_df.rename(columns={'SERVICE_TYPE':'Exp_SERVICE_TYPE',
                                   'CALL_TYPE':'Exp_CALL_TYPE',
                                   'AR_ROUNDED_PRICE':'Exp_AR_ROUNDED_PRICE'}, inplace=True)
    #exp_bhn_df.drop('CALL_TYPE',axis=1, inplace=True)

try:
    if a_BHN_df.empty != True:
        a_BHN_df['AccountNum'] = a_BHN_df.AccountNum.astype(np.int64)
        a_BHN_df['ChargeNumber'] = a_BHN_df.ChargeNumber.astype(np.int64)
        a_BHN_df.rename(columns={'AccountNum':'ACCOUNT_NUMBER',
                                   'ChargeNumber':'CHARGE_NUMBER'}, inplace=True)


        BHN_df = pd.merge(a_BHN_df, exp_bhn_df, how='outer', on=['ACCOUNT_NUMBER','CHARGE_NUMBER'])
        BHN_df['Result'] = BHN_df.apply(compareResults, axis=1)
    else:
        BHN_df = exp_bhn_df
except AttributeError:
    pass


#### CSG Data mapping
exp_csg_df = pd.DataFrame()
CSG_df = pd.DataFrame()
if res_df.iloc[0]['BILLER'] == 'CSG':
    exp_csg_RefCol = ['BILLER','ACCOUNT_NUMBER','CHARGE_NUMBER','SERVICE_TYPE','ACCOUNT_TYPE','CALL_TYPE',
                      'CREDIT_DEBIT_IND','AR_ROUNDED_PRICE']
    exp_csg_df = res_df.filter(exp_csg_RefCol)
    #exp_csg_df['CALL_TYPE'] = exp_csg_df.apply(getCallType_BHN, axis=1)
    #exp_csg_df['SERVICE_TYPE'] = exp_csg_df.apply(getServiceType_BHN, axis=1)
    #exp_csg_df['AR_ROUNDED_PRICE'] = exp_csg_df['AR_ROUNDED_PRICE'].\
     #   apply(lambda x: (str(format(x, '.2f')).split('.')[0]+str(format(x,'.2f')).split('.')[1]).zfill(7))
    #exp_csg_df.drop(['CREDIT_DEBIT_IND','ACCOUNT_TYPE'], axis=1, inplace=True)
    exp_csg_df.rename(columns={'SERVICE_TYPE':'Exp_SERVICE_TYPE',
                                   'CALL_TYPE':'Exp_CALL_TYPE',
                                   'AR_ROUNDED_PRICE':'Exp_AR_ROUNDED_PRICE'}, inplace=True)
    #exp_bhn_df.drop('CALL_TYPE',axis=1, inplace=True)

try:
    if a_CSG_df.empty != True:
        a_CSG_df['AccountNum'] = a_CSG_df.AccountNum.astype(np.int64)
        a_CSG_df['ChargeNumber'] = a_CSG_df.ChargeNumber.astype(np.int64)
        a_CSG_df.rename(columns={'AccountNum':'ACCOUNT_NUMBER',
                                   'ChargeNumber':'CHARGE_NUMBER'}, inplace=True)

        print("Colmn:",exp_csg_df.columns)
        CSG_df = pd.merge(a_CSG_df, exp_csg_df, how='outer', on=['ACCOUNT_NUMBER','CHARGE_NUMBER'])
        CSG_df['Result'] = CSG_df.apply(compareResults, axis=1)
    else:
        CSG_df = exp_csg_df
except AttributeError:
    pass
#print(sum_result_df)

### Write to output file
try :
    writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
    sum_result_df.to_excel(writer,'RecCount Summary', index=False)
    if (len(BHN_df) > 1 ):
        BHN_df.to_excel(writer,'BHN', index=False)
    if (len(CSG_df) > 1 ):
        CSG_df.to_excel(writer,'CSG', index=False)
    if (len(a_ICOMS_df) > 1 ):
        a_ICOMS_df.to_excel(writer,'TWC_ICOMS', index=False)
    if (len(a_NYC_df) > 1 ):
        a_NYC_df.to_excel(writer,'NYC', index=False)
    all_df.to_excel(writer, 'All_Records', index=False)
    res_df.to_excel(writer, 'Aggr_Records', index=False)
    writer.save()

except PermissionError:
    print("\nERROR:")
    print("Please close file:'" + os.path.basename(OUTPUT_FILE) + "' and try again")
    exit(-1)

except Exception as e:
    print("\nERROR:", e)
    print("Please close file:'" + os.path.basename(OUTPUT_FILE) + "' and try again")
    exit(-1)


print("\nOutputfile:" + OUTPUT_FILE)
"""