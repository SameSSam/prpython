import socket
import threading

#port mapping configuration
CFG_REMOTE_IP = '192.168.1.135'
CFG_REMOTE_PORT = 9100
CFG_LOCAL_IP = '0.0.0.0'
CFG_LOCAL_PORT = 8080

#define cache size
PKT_BUFF_SIZE = 2048

#log info
def send_log (content) :
     return print(content)

#one_way data transmission
def tcp_mapping_worker(conn_receiver,conn_sender) :
    round_count=0
    while True:
        try:
            data = conn_receiver.recv(PKT_BUFF_SIZE)
        except Exception:
            send_log('Event: Connection Closed.')

            break
        if not data :
            send_log('Info: No More Data is Received.')
            send_log('Agent is Waiting for your next request......')
            break
      
        try:
            conn_sender.sendall(data)
            round_count+=1
            if round_count ==1 :
                print('No1 data is:', data)
            send_log('No--%d Info: Mapping > %s -> %s > %d bytes.' %(round_count,conn_receiver.getpeername(),conn_sender.getpeername(),len(data)))
        except Exception:
            send_log('Error: Failed sending data.')
            break
        
#        round_count+=1
#        send_log('No--%d Info: Mapping > %s -> %s > %d bytes.' %(round_count,conn_receiver.getpeername(),conn_sender.getpeername(),len(data)))
    conn_receiver.close()
    print('socket to RECV closed.')
    conn_sender.close()
    print('socket to SEND closed.')
    return

#mapping request
def tcp_mapping_request(local_conn,remote_ip,remote_port) :
    remote_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        remote_conn.connect((remote_ip,remote_port))
        print('socket to printer established.')
    except Exception:
        local_conn.close()
        send_log('Error: Unable to connect to the remote server.')
        return
    threading.Thread(target=tcp_mapping_worker,args=(local_conn,remote_conn)).start()
    threading.Thread(target=tcp_mapping_worker,args=(remote_conn,local_conn)).start()
    return

#port mapping
def tcp_mapping(remote_ip,remote_port,local_ip,local_port):
    local_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    local_server.bind((local_ip,local_port))
    local_server.listen(1)
    print('Socket listening:...')
    send_log('Event:Starting mapping service on ' + local_ip + ':' + str(local_port) + '...')
    
    while True:
        try: 
            local_conn,local_addr = local_server.accept()
        except (KeyboardInterrupt,Exception):
            local_server.close()
            send_log('Event:Stop Mapping Service.')
            break
        threading.Thread(target=tcp_mapping_request,args=(local_conn,remote_ip,remote_port)).start()
        send_log('Event: Receive Mapping Request from %s:%d.' %local_addr)
    
    return

#main function
if __name__ =='__main__' :
    tcp_mapping(CFG_REMOTE_IP,CFG_REMOTE_PORT,CFG_LOCAL_IP,CFG_LOCAL_PORT)
    