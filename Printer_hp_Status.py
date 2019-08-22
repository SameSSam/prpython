import socket
import os
import time


host = '192.168.2.33'
port = 9100
mySocket = socket.socket()
mySocket.connect((host,port))
esc = '\x1B%-12345X' 
PJL = '@PJL \r\n' 
# COMMAND = '@PJL INFO ID\r\n'  #ok
# COMMAND = '@PJL INFO STATUS\r\n' #ok
# COMMAND = '@PJL INFO USTATUS\r\n'  #ok
COMMAND = '@PJL INFO CONFIG\r\n'  #ok
#test above commands while printer is ready and no problem
# COMMAND = '@PJL INFO STATUS \r\n' 
ECHO = '@PJL ECHO TESTING USTATUS 2019:08:06 \r\n'

mySocket.send(esc.encode()) 
mySocket.send(PJL.encode())
mySocket.send(ECHO.encode())
mySocket.send(COMMAND.encode())
mySocket.send(esc.encode())

# data = mySocket.recv(1024).decode()
# print(data)

data = mySocket.recv(1024).decode()
print(data)
print('Getting More Data from PRINTER>>>>>>>>>')
time.sleep(1)

 
# while True :
# 	data = mySocket.recv(1024).decode()
# 	print(data)
# 	print("Getting More Data from Printer.............")
# 	if not data :
# 		break


mySocket.close()
print('socket is closed!')
