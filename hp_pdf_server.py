#-*- coding:UTF-8 -*-
import socket,time,struct,os,threading
import subprocess

host = '0.0.0.0'
port = 8080

printer_ip = '192.168.2.33'
printer_port = 9100

pdf_dirname = '/tmp/pdffiles/'
ps_dirname = '/tmp/psfiles/'

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
    job_lang =  '@PJL ENTER LANGUAGE = PCL \r\n' 

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
            local_conn.settimeout(5)
            fileinfo_size = struct.calcsize('128si')
            buf = local_conn.recv(fileinfo_size)
            if buf :
                print("start pdf transfering")
                filename,filesize = struct.unpack('128si',buf)
                filename = filename.decode().strip(b'\x00'.decode())
                print(filename)
                #保存pdf文件到指定目录
                file_new = os.path.join(pdf_dirname,('new_' + filename))
                print('New file name %s is saved, and filesize is %s' %(file_new,filesize))
                #接收文件数据内容
                recv_size = 0
                file = open(file_new,'wb')
                print('starting receving data from client....')
                while not recv_size == filesize :
                    if filesize - recv_size > 2048 :
                        rdata = local_conn.recv(2048)
                        recv_size += len(rdata)
                    else :
                        rdata = local_conn.recv(filesize - recv_size)
                        recv_size = filesize
                    file.write(rdata)
                file.close()
                print('One pdf file transfered!')   
                #接收完一个文件
                #optimize pdf file
                pdf_file_opt = os.path.join(pdf_dirname,('opt_' + str(file_count) + '.pdf'))
                # os.system("gs -o " + file_opt +" -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dPDFSETTINGS=/default -dEmbedAllFonts=false -dCompressFonts=true -dCompatibilityLevel=1.6 -dDetectDuplicateImages=true " + file_new)
                # subprocess.call("gs -o " + pdf_file_opt +" -sDEVICE=pdfwrite -dSAFER -dNOPAUSE -dBATCH -dPDFSETTINGS=/default -dEmbedAllFonts=true -dCompressFonts=true -dCompatibilityLevel=1.6 -dDetectDuplicateImages=true " + file_new, shell = True)
                subprocess.call("gs -dNOPAUSE -dBATCH -dPARANOIDSAFER -dNOINTERPOLATE -sDEVICE=ljet4 -sOutputFile=" + pdf_file_opt + " -f" + file_new, shell = True)
                file_count += 1
                # time.sleep(0.7)
                ###convert pdf file to ps file, store in the ps files folder.
                #hide block below to stop pdf convert,block start
                #***********************************************
                # ps_file_count += 1
                # print("ps_file_count is %s" %file_count)                
                # ps_filename = ps_dirname + 'ps_' + str(file_count) + '.ps'
                # os.system("pdftops -level3 " + file_new +' ' + ps_filename)
                # subprocess.call("pdftops -level3 " + file_new +' ' + ps_filename, shell = True)
                # os.system("pdftops -level3 " + file_opt +' ' + ps_filename)
                # subprocess.call("pdftops -level3 " + pdf_file_opt +' ' + ps_filename, shell = True)
                # subprocess.call("pdf2ps -dLanguageLevel=3 " + file_opt +' ' + ps_filename, shell = True)
                # time.sleep(0.4)
                # print('One pdf file Converted to pclfile: %s ' %ps_filename)
                #***********************************************
                #pdftops block end
                #开始发送ps文件字节流到打印机, 通过函数实现，有两个参数，一个是文件名，一个是连接名。
                #如果这是第一个PS文件，需要初始化，否则直接发送文件内容；如果是最后一个文件，需要首先结束作业。
                # remote_conn = conn_to_printer(printer_ip,printer_port)
                start_time = time.time()
                if file_count == 1000001 :
                    conn_bytes_stream(remote_conn,pr_msg_init())
                    conn_bytes_stream(remote_conn,pr_status_job_start())
                    ps_bytes_to_printer(remote_conn,pdf_file_opt)
                else :
                    # conn_bytes_stream(remote_conn,pr_msg_init_ps())
                    ps_bytes_to_printer(remote_conn,pdf_file_opt)
                cost_time = time.time()-start_time
                print("Time cost to print is %f" %cost_time)
        except socket.timeout :
            break
    print('file tranfer completed, send end job command to the printer.')
    conn_bytes_stream(remote_conn,pr_status_job_end())  
    final_file_count = file_count - 1000000
    print(' file transfer loop is end because of timeout, the last file number is %s' %final_file_count)

# 主程序开始
if __name__ == '__main__':
    os_mkdir(pdf_dirname)
    clean_dir(pdf_dirname)
    os_mkdir(ps_dirname)
    clean_dir(ps_dirname)
    #以上准备系统目录
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(1)
    while True :
        clean_dir(pdf_dirname)
        clean_dir(ps_dirname)
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

   