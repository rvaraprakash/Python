import numpy as np

import pandas as pd
from datetime import datetime
import re
import xlrd
from openpyxl import Workbook

outfile="C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\Output_ChargeFileValidation.xlsx"
BL_RATED_filename = "C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\BL_RATED.csv"
df = pd.read_csv(BL_RATED_filename)

BillingInfoFile="C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\BillingSystemInfo.xlsx"
BI_DF = pd.read_excel(BillingInfoFile)

clean_df = df[df['AR_ROUNDED_PRICE'] > 0]
clean_df.ACCOUNT_NUMBER = clean_df.ACCOUNT_NUMBER.astype(np.int64)

#### Division code
PRI_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
RES_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
BCP_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
TRKSM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'NYC', 'LNK', 'LXM', 'CTX', 'HWI']
PRISM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'LNK', 'LXM', 'CTX', 'HWI']
PRIMDEV_DIV = ['NYC']

###Key fields
CHRG_KEYS = ['ACCOUNT_NUMBER', 'CHARGE_NUMBER', 'ACCOUNT_TYPE', 'AR_ROUNDED_PRICE', 'CALL_TYPE','CREDIT_DEBIT_IND','CHG_FILENAME']
ACC_SERV_KEYS = ['ACCOUNT_TYPE', 'SERVICE_TYPE']
ICOMS_KEYS = ['FINANCE_ENTITY', 'CREDIT_DEBIT_IND','ACCOUNT_NUMBER','CHARGE_NUMBER','ACCOUNT_TYPE', 'SERVICE_TYPE', 'CALL_TYPE', 'CALL_COMP_CALL_TYPE',
              'TAX_INCLUSIVE_IND','AR_ROUNDED_PRICE','USAGE_CYCLE_END']

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
    print("Tax Ind:", row['TAX_INCLUSIVE_IND'])
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
    if re.findall(r"LOC1|LD1", row['CALL_TYPE']):
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
    print (" ----")
    print(filename)
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
    print("Tax Ind:", row['TAX_INCLUSIVE_IND'])
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
    if re.findall(r"LOC1|LD1", row['CALL_TYPE']):
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
    print(filename)
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


#### PRI Accounts
priAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(PRI_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'T'])
                     & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(priAcc_df)):
    print("PRI Accounts")
    #print(priAcc_df[CHRG_KEYS])
    priAcc_df = priAcc_df.filter(ICOMS_KEYS)
    priAcc_df['fileTime'] = pd.to_datetime(priAcc_df['USAGE_CYCLE_END'])
    priAcc_df['fileTime'] = priAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    priAcc_df['CHG_FILENAME']= priAcc_df.apply(createFile_ICOMS, axis=1)
    priAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(priAcc_df)


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
    print(resAcc_df)

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
    print(bcpAcc_df)


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
    print(trksumAcc_df)

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
    print(primsumAcc_df)

#### PrimdetNYC_Accounts
primdetAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['NYC']) & clean_df['ACCOUNT_TYPE'].isin(['R', 'C'])
                         & clean_df['SERVICE_TYPE'].isin(['B', 'F', 'R'])]
if (len(primdetAcc_df)):
    print("PrimdetNYC_Accounts")
    primdetAcc_df = primdetAcc_df.filter(ICOMS_KEYS)
    primdetAcc_df['fileTime'] = pd.to_datetime(primdetAcc_df['USAGE_CYCLE_END'])
    primdetAcc_df['fileTime'] = primdetAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    primdetAcc_df['CHG_FILENAME'] = primdetAcc_df.apply(createFile_CSG, axis=1)
    primdetAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(primdetAcc_df)

#### National_PRI_Accounts
npriAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(npriAcc_df)):
    print("National_PRI_Accounts")
    npriAcc_df = npriAcc_df.filter(ICOMS_KEYS)
    npriAcc_df['fileTime'] = pd.to_datetime(npriAcc_df['USAGE_CYCLE_END'])
    npriAcc_df['fileTime'] = npriAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    npriAcc_df['CHG_FILENAME'] = npriAcc_df.apply(createFile_NS, axis=1)
    npriAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(npriAcc_df)

#### National_BCP_Accounts
nbcpAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['B', 'F'])]
if (len(nbcpAcc_df)):
    print("National_BCP_Accounts")
    nbcpAcc_df = nbcpAcc_df.filter(ICOMS_KEYS)
    nbcpAcc_df['fileTime'] = pd.to_datetime(nbcpAcc_df['USAGE_CYCLE_END'])
    nbcpAcc_df['fileTime'] = nbcpAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    nbcpAcc_df['CHG_FILENAME'] = nbcpAcc_df.apply(createFile_NS, axis=1)
    nbcpAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(nbcpAcc_df)

#### BHN_RES_Accounts
bhnResAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                        & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(bhnResAcc_df)):
    print("BHN_RES_Accounts")
    bhnResAcc_df = bhnResAcc_df.filter(ICOMS_KEYS)
    bhnResAcc_df['fileTime'] = pd.to_datetime(bhnResAcc_df['USAGE_CYCLE_END'])
    bhnResAcc_df['fileTime'] = bhnResAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    bhnResAcc_df['CHG_FILENAME'] = bhnResAcc_df.apply(createFile_ICOMS, axis=1)
    bhnResAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(bhnResAcc_df)

#### BHN_COM_Accounts
bhnComAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                        & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(bhnComAcc_df)):
    print("BHN_COM_Accounts")
    bhnComAcc_df = bhnComAcc_df.filter(ICOMS_KEYS)
    bhnComAcc_df['fileTime'] = pd.to_datetime(bhnComAcc_df['USAGE_CYCLE_END'])
    bhnComAcc_df['fileTime'] = bhnComAcc_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    bhnComAcc_df['CHG_FILENAME'] = bhnComAcc_df.apply(createFile_ICOMS, axis=1)
    bhnComAcc_df.drop(['fileTime'], axis=1, inplace=True)
    print(bhnComAcc_df)

### Combine all DF's
frames = [priAcc_df, resAcc_df, bcpAcc_df, trksumAcc_df, primsumAcc_df, primdetAcc_df, npriAcc_df, nbcpAcc_df, bhnResAcc_df, bhnResAcc_df]
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
res_df.rename(columns={'AR_ROUNDED_PRICE_y':'Exp_AR_ROUNDED_PRICE'}, inplace=True)


### Write to output file
writer = pd.ExcelWriter(outfile)
all_df.to_excel(writer,'All_Records', index=False)
res_df.to_excel(writer,'Aggr_Records', index=False)
writer.save()

"""
# df1 = trksum_df[(trksum_df['DIVISION_CODE']=='NYC') & (trksum_df['SERVICE_TYPE']=='T')]
# print(df1[['ACCOUNT_NUMBER','CHARGE_NUMBER','AR_ROUNDED_PRICE']])

### Sum AR_PRICE based on same account/charge num
# df2= df1.groupby(['ACCOUNT_NUMBER','CHARGE_NUMBER'])['AR_ROUNDED_PRICE'].sum()

# print(df2)

"""
