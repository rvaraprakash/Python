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
