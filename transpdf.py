#-*- coding: UTF-8 -*-
import socket,os,struct,time,threading

def conn_send(conn) :
	file_dir = "D:\\tmp\\pdffiles\\Manualpdf\\"
	filelists = [files for root,dirs,files in os.walk(file_dir)]
	for file in filelists[0][0:25] : 
		if file :
			fileinfo_size = struct.calcsize('128si')
			filesize = os.stat(file_dir+file).st_size
			print(filesize)
			fhead = struct.pack('128sl',file.encode(),filesize)
			conn.sendall(fhead)
			print('%s fhead send out...' %file)
			filerb = open(file_dir + file,'rb')
			while True :
				pdfdata = filerb.read(1024)
				if not pdfdata :
					break
				conn.sendall(pdfdata)
			filerb.close()
			print("pdf file is sent over to the agent server~!")
def conn_recv(conn) :
	while True :
		eot_ack = conn.recv(1024)
		print('reading status from printer................')
		print(eot_ack)
		if b'END' in eot_ack :
			break
	

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(('192.168.30.244',8080))
	threading.Thread(target = conn_send,args = (s,)).start() 
	t=threading.Thread(target=conn_recv,args = (s,))
	t.start()
	t.join()
	s.close()  
	print('File printed completed. Socket closed')          

