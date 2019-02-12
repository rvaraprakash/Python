a = 5
b = 2

try:
  print("resource Open")
  a/b

except Exception as e:
  print("Got Exception:", e)
  
finally:
  print("Resource closed")
