a = 5
b = 2

try:
  print("resource Open")
  a/b

except Exception as e:
  print("Got Exception:", e)
  
finally:
  print("Resource closed")
  
  https://www.martymusic.com
    
  ### Updating dataframe column based on other column
  ## Example update CREDIT_DEBIT_IND = D if CALL_TYPE=LD2
  tmp_df.loc[tmp_df['CALL_TYPE'] == 'LD2', ['CREDIT_DEBIT_IND']]='D'
  
  ## Update CREDIT_DEBIT_IND, TAX_INCLUSIVE_IND if CALL_TYPE=LD2
  tmp_df.loc[tmp_df['CALL_TYPE'] == 'LD2', ['CREDIT_DEBIT_IND', 'TAX_INCLUSIVE_IND']]=['D', 0]
  
  ### Concate dictionaries
  
dict1 = {1: ‘a’, 2:'b', 3:’c’}

dict2 = {1:'d',2:'e'}

{i:j for i in dict1.keys() for j in zip(dict1.values(),dict2.values())}

Results in tuple:

{1: (‘a’,’d’), 2: (‘b’, ‘e’),3:(‘c’)}

If you wish to have in list

{i:list(j)

for i in dict1.keys()

for j in zip(dict1.values(),dict2.values())}

gives:

{1: [‘a’,’d’], 2: [‘b’, ‘e’],3:[‘c’]}·
