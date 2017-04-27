#!usr/bin/python
from socket import *
import hashlib

 
host1 = '100.64.74.2' # '127.0.0.1' can also be used
port1 = 52000
host2 = '100.64.74.3'
port2 = 52001
host3 = '100.64.74.4'
port3 = 52002
sock1 = socket()
sock2 = socket()
sock3 = socket()
#Connecting to socket
sock1.connect((host1, port1)) #Connect takes tuple of host and port
sock2.connect((host2,port2))
sock3.connect((host3,port3))
file1=raw_input('Enter File name :')
text=open(file1,'r').read()

hash_object=hashlib.md5(file1)
m=hash_object.hexdigest()
n=int(m,16)%3

 
#Infinite loop to keep client running.
while True:
    if n==0:
            sock1.send('Hi I am loadbalncer')
            data1=sock1.recv(1024)
            print data1
          
    elif n==1:
            sock2.send('Hi I am client')
            data2=sock2.recv(1024)
            print data2
                 
    elif n==2:
            sock3.send('Hi I am client')
            data3=sock3.recv(1024)
            print data3
    
   
 
sock.close()
