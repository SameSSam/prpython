#-*- coding:UTF-8 -*-
import socket,time,struct,os,threading
import subprocess

host = '0.0.0.0'
port = 8080

printer_ip = '192.168.2.33'
printer_port = 9100

img_dirname = '/tmp/img/'

#如系统目录不存在，则先创建
def os_mkdir(dirname) :
    if not os.path.exists(dirname) :
        os.system('mkdir -p ' + dirname)

def clean_dir(dirname) :
    if os.path.exists(dirname) :
        os.system('rm -fr ' + dirname + '*')

def pr_eot_ack(conn_server, conn_printer) :
    while True :
        eot_ack = conn_printer.recv(2048)
        conn_server.sendall(eot_ack)
        print('reading status from printer and send to client................')
        print(eot_ack)
        if b'END' in eot_ack :
            break
    conn_printer.close()

def pr_msg_init():
    msg_init = '\x1B%-12345X@PJL\r\n' 
    return msg_init

def pr_msg_init_ps() :
    return pr_msg_init() + "@PJL ENTER LANGUAGE = PDF \r\n"


def conn_bytes_stream(conn, stream_bytes) :
    conn.sendall(stream_bytes.encode())

def pr_msg_end() :
    msg_end = '\x1B%-12345X' 
    return msg_end

#job start bytes
def pr_status_job_start() :
    job_comment = '@PJL COMMENT **Beginning of Job ** \r\n'
    job_name = '@PJL JOB NAME="PDF_JOB PRINTGING STARTING" \r\n'
    job_ustatus = '@PJL USTATUS JOB=ON \r\n' \
                  '@PJL USTATUS DEVICE = ON \r\n'
    job_lang =  '@PJL ENTER LANGUAGE = POSTSCRIPT \r\n' 

    job_start_str = job_comment + job_name + job_ustatus + job_lang
    return job_start_str
#job end bytes
def pr_status_job_end() :
    job_eoj = '@PJL EOJ NAME ="End of PostScript File Printing" \r\n'
    return (pr_msg_end() + pr_msg_init() + job_eoj + pr_msg_end())
#socket connection to printer
def conn_to_printer(host,ip) :
    remote_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_conn.connect((host,ip))
    return remote_conn

def ps_bytes_to_printer(conn,filename) :
    #file data send to printer start
    try:
        file_bytes = open(filename,'rb')
        # while True :
        #     ps_data = file_bytes.read(1024)
        #     if not ps_data :
        #         break
        #     conn.sendall(ps_data)
        conn.sendfile(file_bytes,0)
        file_bytes.close()
        print("pdf %s file send to printer!!!" %filename)
    except IOError as e :
        print('file IO Error: ', e)

def conn_send_mapping(local_conn, remote_conn) :
    file_count = 1000000
    while True :
        try :
            local_conn.settimeout(3)
            img_link_bytes = local_conn.recv(1024)
            print(img_link_bytes)
            print(bytes.decode(img_link_bytes))
            if img_link_bytes :
                img_link_http = bytes.decode(img_link_bytes)  #.strip(b'\x00'.decode())
                print("The img link from customer is %s:" %img_link_http)
                #通过系统下载文件，文件保存在/tmp/image目录下
                subprocess.call("wget -P " + img_dirname + ' ' + img_link_http, shell = True)
                file_count += 1
                #查看目录下文件是否存在
                filelists = [files for root,dirs,files in os.walk(img_dirname)]
                for filename in filelists[0][0:] : 
                    if filename :
                        print('Files Downloaded, Preparing for printing.............')
                        img_file = img_dirname + filename
                        print(img_file)
                        start_time = time.time()
                        if file_count == 1000001 :
                            conn_bytes_stream(remote_conn,pr_msg_init())
                            conn_bytes_stream(remote_conn,pr_status_job_start())
                            ps_bytes_to_printer(remote_conn,img_file)
                        else :
                            # conn_bytes_stream(remote_conn,pr_msg_init_ps())
                            ps_bytes_to_printer(remote_conn,img_file)
                        cost_time = time.time()-start_time
                        print("Time cost to print is %f" %cost_time)
                    else :
                        print("NO FILES DOWNLOADED!!!")
                # remote_conn = conn_to_printer(printer_ip,printer_port)
                
        except socket.timeout :
            break
    print('file tranfer completed, send end job command to the printer.')
    conn_bytes_stream(remote_conn,pr_status_job_end())  
    final_file_count = file_count - 1000000
    print(' file transfer loop is end because of timeout, the last file number is %s' %final_file_count)

# 主程序开始
if __name__ == '__main__':
    os_mkdir(img_dirname)
    clean_dir(img_dirname)
    #以上准备系统目录
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(1)
    while True :
        clean_dir(img_dirname)
        # remote_conn = conn_to_printer(printer_ip,printer_port)
        print('Agent Server is starting new session-----------')
        local_conn,address = s.accept()
        print('Connected by Client: %s %s' %address)
        remote_conn = conn_to_printer(printer_ip,printer_port)
        threading.Thread(target=conn_send_mapping,args=(local_conn,remote_conn)).start()
        t=threading.Thread(target=pr_eot_ack,args = (local_conn,remote_conn))
        t.start()
        t.join()
        # remote_conn.close()
        print('socket to printer closed.')
        local_conn.close()  
        print('File printed completed. Socket closed')          

   