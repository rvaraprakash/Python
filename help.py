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




#### Highlight color

df = pd.DataFrame({'Val1':['PASS','FAIL','PASS'], 'Col2':['PASS','PASS','FAIL']})

def color_red(val):
    color = 'red' if val == 'FAIL' else 'black'
    return 'color: %s' % color
 
def highlight_red(row):
    return ['background-color: red' if v == 'FAIL' else 'background-color: green' for v in row]
  
 df.style.applymap(color_red)


df.style.apply(highlight_red, subset=pd.IndexSlice[:, ['Val1']])
