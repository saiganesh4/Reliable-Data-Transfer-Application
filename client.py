
import pickle
import hashlib
import socket
import threading 

#creating and binding socket to receive the messages sent by server
server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(("",4444))

#creating the socket to send the messages to the server
send_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client = ("192.168.53.102",5555) #ip address and port number of server

#receiving message from the server
msg,addr = server.recvfrom(1024)
print(msg.decode())

NO_OF_THREADS = 500
timeout = 0.3        #in sec
buff_size = 4096     #packet size

#Reading the data of length packet size and storing it in the list.
List_of_data=[]
with open ("CS3543_100MB","rb") as file:
    data = file.read(buff_size)
    while data:
        List_of_data.append(data)
        data = file.read(buff_size)
print(len(List_of_data))

#Packet header
class packet:
    def __init__(self, ack_seq, data, number, check_sum):
        self.ack_seq=ack_seq
        self.data=data
        self.packet_num=number
        self.check_sum=check_sum

class packet1:
    def __init__(self,ack_seq,check_sum):
        self.ack=ack_seq
        self.check_sum=check_sum

List_of_threads=[]
List_of_events=[]
List_of_waiting_seq=[]
flag=False

#function executed by the threads
def task(id):
    no=id 
    seq=0
    print(id)
    length_buffer = len(List_of_data)
    first_time = 1
    while True:
        if id == 0 and first_time == 1:
            data_to_send = pickle.dumps(packet(id*10+seq, length_buffer, -1, hashlib.md5(str(length_buffer).encode()).digest()))
            send_sock.sendto(data_to_send,client)
            check = List_of_events[id].wait(timeout)
            List_of_events[id].clear()

            List_of_waiting_seq[id] = seq

            #if ack received
            if check:
                seq = 1-seq
                first_time = 0

        else:
            if no >= length_buffer or flag == True:
                return
            data_to_send = pickle.dumps(packet(id*10+seq, List_of_data[no], no, hashlib.md5(List_of_data[no]).digest()))
            send_sock.sendto(data_to_send,client)

            check = List_of_events[id].wait(timeout)
            List_of_events[id].clear()

            List_of_waiting_seq[id] = seq

            #if ack received
            if check:
                seq = 1-seq
                no = no+NO_OF_THREADS


if __name__ == "__main__":

    #creating the threads
    for i in range(NO_OF_THREADS):
        List_of_threads.append(threading.Thread( target=task, args=(i,) ) )
        List_of_events.append(threading.Event())
        List_of_waiting_seq.append(0)

    for thread in List_of_threads:
        thread.start()
    

    #Main threads receives Acks and notifies the worker threads
    while True:
        msg,addr = server.recvfrom(512)
        msg = pickle.loads(msg)  #receives Ack

        #server sends '-1' to tell the client that the file has been received. 
        if msg.ack == -1:
            flag = True
            print("Finished")
            break

        thread_id,seq_rev = msg.ack//10 , msg.ack%10
        
        if seq_rev == List_of_waiting_seq[thread_id] and msg.check_sum == hashlib.md5(str(msg.ack).encode()).digest():
            List_of_events[thread_id].set()   #notifying the corresponding worker thread


    for thread in List_of_threads:
        thread.join()
