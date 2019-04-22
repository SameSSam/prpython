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

def pr_eot_ack(conn_server, conn_printer) :
    while True :
        eot_ack = conn_printer.recv(1024)
        conn_server.sendall(eot_ack)
        print('reading status from printer and send to client................')
        print(eot_ack)
        if b'END' in eot_ack :
            break

def pr_msg_init():
    msg_init = '\x1B%-12345X@PJL\r\n' \
                '@PJL SET PERSONALITY=POSTSCRIPT\r\n'
                # '@PJL COMMENT Set PS for POSTSCRIPT printing\r\n' \
                # '@PJL SET PERSONALITY=POSTSCRIPT\r\n'
                # '@PJL SET DUPLEX=OFF\r\n' \
                # '@PJL ENTER LANGUAGE = POSTSCRIPT\r\n'
    return msg_init

def conn_bytes_stream(conn, stream_bytes) :
    conn.sendall(stream_bytes.encode())

def pr_msg_end() :
    msg_end = '\x1B%-12345X' 
    return msg_end

#job start bytes
def pr_status_job_start() :
    job_comment = '@PJL COMMENT **Beginning of Job ** \r\n'
    job_name = '@PJL JOB NAME="PS_JOB" \r\n'
    job_ustatus = '@PJL USTATUS JOB=ON \r\n' \
                  '@PJL USTATUS DEVICE = VERBOSE \r\n'
    job_lang =  '@PJL ENTER LANGUAGE = POSTSCRIPT \r\n' \

    job_start_str = job_comment + job_name + job_ustatus + pr_msg_init() + job_lang
    return job_start_str
#job end bytes
def pr_status_job_end() :
    job_eoj = '@PJL EOJ NAME ="End of PostScript File Printing" \r\n'
    return (pr_msg_end() + pr_msg_init() + job_eoj)
#socket connection to printer
def conn_to_printer(host,ip) :
    remote_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_conn.connect((host,ip))
    return remote_conn

# def messagePSStart() :
#     messagePSStart_Msg = '\x1B%-12345X@PJL\r\n' \
#                 '@PJL COMMENT Set PS for PS printing\r\n' \
#                 '@PJL SET PERSONALITY=POSTSCRIPT\r\n' \
#                 '@PJL SET DUPLEX=OFF\r\n' \
#                 '@PJL ENTER LANGUAGE = POSTSCRIPT\r\n'

#     return messagePSStart_Msg

# def messagePSEnd() :
#     messagePSEnd_Msg = '\x1B%-12345X@PJL \r\n@PJL RESET \r\n\x1B%-12345X'
#     return messagePSEnd_Msg

def ps_bytes_to_printer(conn,filename) :
    conn.send(messagePSStart().encode())
    file_bytes = open(filename,'rb')
    while True :
        ps_data = file_bytes.read(1024)
        if not ps_data :
            break
        conn.sendall(ps_data)
    file_bytes.close()
    print("ps %s file send to printer!!!" %filename)
    conn.send(messagePSEnd().encode())

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
                
                file_new = os.path.join(pdf_dirname,('new_' + filename))

                print('New file name is %s, and filesize is %s' %(file_new,filesize))
                #接收文件数据内容
                recv_size = 0
                file = open(file_new,'wb')
                print('starting receving data from client....')
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
                
                ps_filename = ps_dirname + 'ps_' + str(ps_file_count) + '.ps'
                os.system("pdftops -level3 " + file_new +' ' + ps_filename)
                print('One pdf file Converted to psfile: %s ' %ps_filename)

                #开始发送ps文件字节流到打印机, 通过函数实现，有两个参数，一个是文件名，一个是连接名。
                #如果这是第一个PS文件，需要初始化，否则直接发送文件内容；如果是最后一个文件，需要首先结束祖业。
                remote_conn = conn_to_printer(printer_ip,printer_port)
                if ps_file_count == 1000001 :
                    conn_bytes_stream(remote_conn,pr_msg_init())
                    conn_bytes_stream(remote_conn,pr_status_job_start())
                    ps_bytes_to_printer(remote_conn,ps_filename)
                else :
                    ps_bytes_to_printer(remote_conn,ps_filename)
            else :
                conn_bytes_stream(remote_conn,pr_status_job_end())
                conn_bytes_stream(remote_conn,pr_msg_end())
                # connection.close()
                final_psfile_count = ps_file_count-1000000
                print('socket is closed because of timeout, the last file number is %s' %final_psfile_count)
                break
            


        except socket.timeout :
            connetion.close()
            

#主程序开始
if __name__ == '__main__':
    os_mkdir(pdf_dirname)
    os_mkdir(ps_dirname)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(1)
    while True :
        print('Agent Server is starting new session-----------')
        connection,address = s.accept()
        print('Connected by Client: %s %s' %address)
        threading.Thread(target=conn_thread,args=(connection,address)).start()
        t=threading.Thread(target=pr_eot_ack,args = (connection,remote_conn))
        t.start()
        t.join()
        remote_conn.close()
        connetion.close()  
        print('File printed completed. Socket closed')          

   