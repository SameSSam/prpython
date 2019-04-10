import time
ESC = '\x1B%-12345X' 
PJL = '@PJL \r\n' 

def pr_msg_init():
	msg_init = '\x1B%-12345X@PJL\r\n' \
				'@PJL SET PERSONALITY=POSTSCRIPT\r\n'
				# '@PJL COMMENT Set PS for POSTSCRIPT printing\r\n' \
				# '@PJL SET PERSONALITY=POSTSCRIPT\r\n'
				# '@PJL SET DUPLEX=OFF\r\n' \
				# '@PJL ENTER LANGUAGE = POSTSCRIPT\r\n'
	return msg_init

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

#single file send to socket
def file_bytes_stream(conn,postscript_file) :
	bytes_file = open(postscript_file,'rb')
	while True :
		bytes_stream = bytes_file.read(1024)
		if not bytes_stream :
			break
		conn.sendall(bytes_stream)
	bytes_file.close()

def pr_status_read(conn) :
	while True :
		recv_data = conn.recv(1024)
		if not recv_data :
			break
	return print(recv_data)

def eot_ack(conn) :
	while True :
		eot_ack = conn.recv(1024)
		print('reading status from printer................')
		print(eot_ack)
		# if eot_ack == b'\x04':
		if eot_ack == b'' :
			break
		# else :
		# 	print('No data received.')
		# 	break

def send_to_pr(conn, filename) :
	conn.send(pr_msg_init().encode())
	conn.send(pr_status_job_start().encode())
	file_bytes_stream(conn,filename)
	conn.send(pr_msg_end().encode())
	
	

	



	 