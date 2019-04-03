#-*- coding:UTF-8 -*-
import socket,time,struct,os,threading

host = '0.0.0.0'
port = 8080

printer_ip = '192.168.1.111'
printer_port = 9100

pdf_dirname = '/tmp/pdffiles/'
ps_dirname = '/tmp/psfiles/'

#如系统目录不存在，则先创建
def os_mkdir(dirname) :
    if not os.path.exists(dirname) :
        os.system('mkdir -p ' + dirname)

#socket connection to printer
def conn_to_printer(host,ip) :
    remote_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_conn.connect((host,ip))
    return remote_conn

def ps_bytes_to_printer(conn,filename) :
    file_bytes = open(filename,'rb')
    while True :
        ps_data = file_bytes.read(1024)
        if not ps_data :
            break
        conn.sendall(ps_data)
    file_bytes.close()
    print("ps %s file send to printer!!!" %filename)

def conn_thread(connection, address) :
    ps_file_count = 1000000
    while True :
        try :
            connection.settimeout(3)
            fileinfo_size = struct.calcsize('128si')
            buf = connection.recv(fileinfo_size)
            if buf :
                print("start pdf transfering")
                filename,filesize = struct.unpack('128si',buf)
                filename = filename.decode().strip(b'\x00'.decode())
                print(filename)
                #保存pdf文件到指定目录
                os_mkdir(pdf_dirname)
                file_new = os.path.join(pdf_dirname,('new_' + filename))

                print('New file name is %s, and filesize is %s' %(file_new,filesize))
                #接收文件数据内容
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
                #接收完一个文件
                ###convert pdf file to ps file, store in the ps files folder.
                
                ps_file_count += 1
                print("ps_file_count is %s" %ps_file_count)
                os_mkdir(ps_dirname)
                ps_filename = ps_dirname + 'ps_' + str(ps_file_count) + '.ps'
                os.system("pdftops -level3 " + file_new +' ' + ps_filename)
                print('One pdf file Converted to psfile: %s ' %ps_filename)

                #开始发送ps文件字节流到打印机, 通过函数实现，有两个参数，一个是文件名，一个是连接名。
                remote_conn = conn_to_printer(printer_ip,printer_port)
                ps_bytes_to_printer(remote_conn,ps_filename)
            


        except socket.timeout :
            connetion.close()
            final_psfile_count = ps_file_count-1000000
            print('socket is closed because of timeout, the last file number is %s' %final_psfile_count)
            return final_psfile_count

#主程序开始
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))
s.listen(1)
print('Agent Server is waiting for new session-----------')
while True :
    connection,address = s.accept()
#    print('Connected by Client: %s' %address)
    threading.Thread(target=conn_thread,args=(connection,address)).start()
   