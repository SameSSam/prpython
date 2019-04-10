import socket
import os
import time
import lexlp
import threading

printer_host = '192.168.1.111'
printer_port = 9100

lp_conn = socket.socket()
lp_conn.connect((printer_host,printer_port))

file_dir = "D:\\tmp\\pdffiles\\single_test\\"

def socket_to_printer(conn,file_dir):
#Open printing files with rb and send them to printer:
    conn.send(lexlp.pr_msg_init().encode())
    conn.send(lexlp.pr_status_job_start().encode())
    filenames = [files for root,dirs,files in os.walk(file_dir)]
    for file in filenames[0][0:10] :
#file data send to printer start
        try:
            filename = file_dir + file
            print("The %s pdf file is sent out for printing" %(filenames[0].index(file)+1))
            start_time = time.time()
            lexlp.send_to_pr(conn,filename)
            end_time = time.time()
            print('total printing time cost is %s' %(end_time - start_time))
        except IOError as e :
            print('file IO Error: ', e)
    conn.send(lexlp.pr_status_job_end().encode())

if __name__ == '__main__':
    threading.Thread(target = socket_to_printer,args = (lp_conn,file_dir)).start()
    t=threading.Thread(target=lexlp.pr_eot_ack,args = (lp_conn,))
    t.start()
    t.join()
    lp_conn.close()  
    print('File printed completed. Socket closed')          



    

