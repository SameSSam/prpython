#-*- coding:UTF-8 -*-
import socket,time,struct,os,threading

host = '0.0.0.0'
port = 8080

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))
s.listen(1)

def conn_thread(connection, address) :
    ps_file_count = 1000000
    while True :
        try :
            connection.settimeout(5)
            fileinfo_size = struct.calcsize('128si')
            buf = connection.recv(fileinfo_size)
            if buf :
                print("start pdf transfering")
                filename,filesize = struct.unpack('128si',buf)
                filename = filename.decode().strip(b'\x00'.decode())
                print(filename)
                file_new = os.path.join('/tmp/pdffiles',('new_' + filename))

                print('New file name is %s, and filesize is %s' %(file_new,filesize))
                recv_size = 0
                file = open(file_new,'wb')
                print('starting receving data....')
                while not recv_size == filesize :
                    if filesize - recv_size > 1024 :
                        rdata = connection.recv(1024)
                        recv_size += len(rdata)
                    else :
                        rdata = connection.recv(filesize - recv_size)
                        recv_size = filesize
                    file.write(rdata)
                file.close()
                print('One pdf file transfered!')   

                ###convert pdf file to ps file, store in the ps files folder.
                
                ps_file_count += 1
                print("ps_file_count is %s" %ps_file_count)
                os.system("pdftops -level3 " + file_new +' /tmp/psfiles/ps_' + str(ps_file_count) +'.ps')
                print('One pdf file Converted~')   

            


        except socket.timeout :
            connetion.close()
while True :
    connection,address = s.accept()
#    print('Connected by Client: %s' %address)
    threading.Thread(target=conn_thread,args=(connection,address)).start()
   