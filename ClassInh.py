#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 05:39:14 2019

@author: varaprakashreddy
"""

class A:
    
    def feature1(self):
        print ("Feature1 working..")
        
    def feature2(self):
        print ("Feature2 is working..")
        

class B:
    
    def feature3(self):
        print ("Feature1 working..")
        
    def feature4(self):
        print ("Feature2 is working..")
    

a = A()
a.feature1()
    
### Duck typing    
class pycham:
    def execute(self):
        print("Compiling")
        print("Executing")

class myEditor:
    def execute(self):
        print("Spell check")
        print("Running")

class laptop:
    
    def code(self, ide):
        ide.execute()
        
        

l1 = laptop()
ide = pycham()
ide = myEditor()
l1.code(ide)


#### Operator overloading

class student:
    def __init__(self,m1,m2):
        self.m1=m1
        self.m2=m2
        
    def __add__(self, other):
        m1 = self.m1 + other.m1
        m2 = self.m2 + other.m2
        s3 = student(m1,m2)
        return s3
    
    def __str__(self):
        return '{} {}'.format(self.m1,self.m2)

s1 = student(20,40)
s2 = student(50,60)
s3 = s1 + s2 ### intenrally calls __add__ method
print (s3.m1)
print(s3) ### Internally calls __str__ method