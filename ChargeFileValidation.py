import numpy as np

import pandas as pd
from datetime import datetime
import re

filename = "C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\BL_RATED.csv"
# df = pd.read_csv('C:\Vara\AM&R\scripts\Ref_Scripts\ChargeFileGen\BL_RATED.csv')
df = pd.read_csv(filename)

clean_df = df[df['AR_ROUNDED_PRICE'] > 0]

#### Division code
PRI_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
RES_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
BCP_DIV = ['CAR', 'CVG', 'MKC', 'CMH', 'NEW', 'CAK', 'HNL']
TRKSM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'NYC', 'LNK', 'LXM', 'CTX', 'HWI']
PRISM_DIV = ['NAT', 'NTX', 'SAN', 'STX', 'LNK', 'LXM', 'CTX', 'HWI']
PRIMDEV_DIV = ['NYC']

###Key fields
CHRG_KEYS = ['DIVISION_CODE', 'ACCOUNT_TYPE', 'SERVICE_TYPE', 'SERVICE_TYPE', 'AR_ROUNDED_PRICE', 'FINANCE_ENTITY']
ACC_SERV_KEYS = ['ACCOUNT_TYPE', 'SERVICE_TYPE']


#### Create file
def createFile_ICOMS(row):
    file = row['FINANCE_ENTITY'] + row['fileTime']
    if (row['CREDIT_DEBIT_IND'] == 'D'):
        file = file + "0000"
    else:
        file = file + "0001"

    if (row['SERVICE_TYPE'] == 'R'):
        file = file + ".RESP"
    elif (row['SERVICE_TYPE'] == 'B'):
        file = file + ".BCPP"
    elif (row['SERVICE_TYPE'] == 'T'):
        file = file + ".PRIP"

    if (row['TAX_INCLUSIVE_IND'] == '0'):
        file = file + "taxed"
    else:
        file = file + "untaxed"

    if re.findall(r"DA|CC|OA[1-6]", row['CALL_TYPE']):
        file = file + "1"
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        file = file + "2"
    if re.findall(r"LOC1|LD1", row['CALL_TYPE']):
        file = file + "3"
    if re.findall(r"LOCT2|LD2|LD3|LD7", row['CALL_TYPE']):
        file = file + "4"
    if re.findall(r"LD4|LD5|LD6|INT|TERR[0-99]", row['CALL_TYPE']):
        file = file + "5"
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC1|LOCT1|LD1", row['CALL_COMP_CALL_TYPE']):
        file = file + "6"
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LOC2|LOCT2|LD2|LD3|LD7", row['CALL_COMP_CALL_TYPE']):
        file = file + "7"
    if re.findall(r"OA8", row['CALL_TYPE']) and re.findall(r"LD4", row['CALL_COMP_CALL_TYPE']):
        file = file + "8"
    file+=".txt"
    print(file)


#### PRI Accounts
priAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(PRI_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'T'])
                     & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(priAcc_df)):
    print("PRI Accounts")
    print(priAcc_df[CHRG_KEYS])
    row_df = priAcc_df.filter(
        ['FINANCE_ENTITY', 'CREDIT_DEBIT_IND', 'SERVICE_TYPE', 'CALL_TYPE', 'CALL_COMP_CALL_TYPE', 'TAX_INCLUSIVE_IND',
         'USAGE_CYCLE_END'])

    row_df['fileTime'] = pd.to_datetime(row_df['USAGE_CYCLE_END'])
    row_df['fileTime'] = row_df.fileTime.apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    row_df.drop_duplicates(inplace=True)
    row_df.apply(createFile_ICOMS, axis=1)
    print(row_df)

"""
#### RES Accounts
resAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(RES_DIV) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                     & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(resAcc_df)):
    print("RES Accounts")
    print(resAcc_df[CHRG_KEYS])

#### BCP Accounts
bcpAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(BCP_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'F'])
                     & clean_df['SERVICE_TYPE'].isin(['B', 'F'])]
if (len(bcpAcc_df)):
    print("BCP Accounts")
    print(bcpAcc_df[CHRG_KEYS])

#### Trunksum_Accounts
trksumAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(TRKSM_DIV) & clean_df['ACCOUNT_TYPE'].isin(['C', 'T'])
                        & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(trksumAcc_df)):
    print("Trunksum_Accounts")
    print(trksumAcc_df[CHRG_KEYS])

#### Primsum_Accounts
primsumAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(TRKSM_DIV) & clean_df['ACCOUNT_TYPE'].isin(['R', 'C'])
                         & clean_df['SERVICE_TYPE'].isin(['B', 'F', 'R'])]
if (len(primsumAcc_df)):
    print("Primsum_Accounts")
    print(primsumAcc_df[CHRG_KEYS])

#### PrimdetNYC_Accounts
primdetAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['NYC']) & clean_df['ACCOUNT_TYPE'].isin(['R', 'C'])
                         & clean_df['SERVICE_TYPE'].isin(['B', 'F', 'R'])]
if (len(primdetAcc_df)):
    print("PrimdetNYC_Accounts")
    print(primdetAcc_df[CHRG_KEYS])

#### National_PRI_Accounts
npriAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['T'])]
if (len(npriAcc_df)):
    print("National_PRI_Accounts")
    print(npriAcc_df[CHRG_KEYS])

#### National_BCP_Accounts
nbcpAcc_df = clean_df[clean_df['ACCOUNT_TYPE'].isin(['N']) & clean_df['SERVICE_TYPE'].isin(['B', 'F'])]
if (len(nbcpAcc_df)):
    print("National_BCP_Accounts")
    print(nbcpAcc_df[CHRG_KEYS])

#### BHN_RES_Accounts
bhnResAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                        & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(bhnResAcc_df)):
    print("BHN_RES_Accounts")
    print(bhnResAcc_df[CHRG_KEYS])

#### BHN_COM_Accounts
bhnComAcc_df = clean_df[clean_df['DIVISION_CODE'].isin(['BHN']) & clean_df['ACCOUNT_TYPE'].isin(['R'])
                        & clean_df['SERVICE_TYPE'].isin(['R'])]
if (len(bhnComAcc_df)):
    print("BHN_COM_Accounts")
    print(bhnComAcc_df[CHRG_KEYS])

# df1 = trksum_df[(trksum_df['DIVISION_CODE']=='NYC') & (trksum_df['SERVICE_TYPE']=='T')]
# print(df1[['ACCOUNT_NUMBER','CHARGE_NUMBER','AR_ROUNDED_PRICE']])

### Sum AR_PRICE based on same account/charge num
# df2= df1.groupby(['ACCOUNT_NUMBER','CHARGE_NUMBER'])['AR_ROUNDED_PRICE'].sum()

# print(df2)

"""
