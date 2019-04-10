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
def send_to_pr(conn,postscript_file) :
	bytes_file = open(postscript_file,'rb')
	while True :
		bytes_stream = bytes_file.read(1024)
		if not bytes_stream :
			break
		conn.sendall(bytes_stream)
	bytes_file.close()

def pr_eot_ack(conn) :
	while True :
		eot_ack = conn.recv(1024)
		print('reading status from printer................')
		print(eot_ack)
		if b'END' in eot_ack :
			break
	

	



	 