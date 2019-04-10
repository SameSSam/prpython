import socket
import os
import time



def messagePdfStart() :
	messagePdfStart = '\x1B%-12345X@PJL\r\n' \
				'@PJL COMMENT Set PS for PDF printing\r\n' \
				'@PJL SET PERSONALITY=POSTSCRIPT\r\n' \
				'@PJL SET DUPLEX=OFF\r\n' \
				'@PJL ENTER LANGUAGE = POSTSCRIPT\r\n' \
                '@PJL USTATUS DEVICE = OFF \r\n'

	return messagePdfStart

def messagePdfEnd() :
	messagePdfEnd = '\x1B%-12345X@PJL \r\n@PJL RESET \r\n\x1B%-12345X'
	return messagePdfEnd

def Main():
    host = '192.168.1.111'
    port = 9100
    mySocket = socket.socket()
    mySocket.connect((host,port))
    # mySocket.send(messagePdfStart().encode())

#Open PDF files with rb and send them to printer:
    # file_dir = "C:\\Users\Kaka6\\Documents\\CloudClass\\PDFDOCS\\pdf17\\"
    file_dir = "D:\\tmp\\pdffiles\\single_test\\"
    filenames = [files for root,dirs,files in os.walk(file_dir)]
    for file in filenames[0][0:5] :
#pdfjob start
        try:
            print("The %s pdf file is sent out for printing" %(filenames[0].index(file)+1))
            start_time = time.time()
            mySocket.send(messagePdfStart().encode())
            filerb = open(file_dir+file,'rb')
            while True :
                pdfdata = filerb.read(1024)
                if not pdfdata :
                    break
                mySocket.sendall(pdfdata)
            filerb.close()
            # end_time = time.time()
            mySocket.send(messagePdfEnd().encode())
            eot_ack = mySocket.recv(1024)
            print(eot_ack)
            if eot_ack == b'\x04':
                end_time = time.time()
                print('total time cost is %s' %(end_time - start_time))
                print('file printed out................................')
                continue
            else :
                break
        except IOError as e :
            print('file IO Error: ', e)
    mySocket.close()  
    print('socket is closed')          
#Send Pdf End to printer:
    # mySocket.send(messagePdfEnd().encode())


    # data_recv_total=''
    # while True:
    #     data_recv = mySocket.recv(2048)
    #     print(data_recv)
    #     data_recv_total +=data_recv.decode()
    #     print(data_recv_total,len(data_recv_total))
    #     if len(data_recv_total)==10 :
    #         mySocket.close()
    #         print('socket is closed')
    #         break

if __name__ == '__main__':
    Main()

