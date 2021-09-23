
import pickle
import hashlib
import socket
import threading 
import time

#creating and binding socket to receive the messages sent by client
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.bind(("",5555))

server=("192.168.53.101",4444) #ip address and port number of client

#creating the socket to send the messages to the server
send_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

length_of_buffer=0
send_sock.sendto("hello server".encode(),("192.168.53.101",4444)) #sending message to client
data_to_written=[]

count=0

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

start = time.time()

first_time = 1

#Receiving the packets and sends the acknowlegdment back to the client
while True:

    data_recv,addr = client.recvfrom(4400)

    data_recv = pickle.loads(data_recv)
    if data_recv.packet_num == -1 and first_time == 1 and data_recv.check_sum == hashlib.md5(str(data_recv.data).encode()).digest():
        length_of_buffer = data_recv.data
        for i in range(length_of_buffer):
            data_to_written.append(0)
        first_time = 0
        packet_to_be_sent = packet1(data_recv.ack_seq, hashlib.md5(str(data_recv.ack_seq).encode()).digest())
        packet_to_be_sent = pickle.dumps(packet_to_be_sent)
        send_sock.sendto(packet_to_be_sent,("192.168.53.101",4444))

    elif data_recv.packet_num != -1 and first_time == 0 and data_to_written[data_recv.packet_num] == 0 and data_recv.check_sum == hashlib.md5(data_recv.data).digest():
        count = count+1
        data_to_written[data_recv.packet_num] = data_recv.data
        #print(count)

    if first_time == 0:
        packet_to_be_sent = packet1(data_recv.ack_seq, hashlib.md5(str(data_recv.ack_seq).encode()).digest())
        packet_to_be_sent = pickle.dumps(packet_to_be_sent)
        send_sock.sendto(packet_to_be_sent,("192.168.53.101",4444))

    if count == length_of_buffer:
        break

packet_to_be_sent = packet1(-1, hashlib.md5(str(-1).encode()).digest())
packet_to_be_sent = pickle.dumps(packet_to_be_sent)
send_sock.sendto(packet_to_be_sent,("192.168.53.101",4444))

time_taken = time.time()-start 
print("Time taken = {} secs".format(time_taken))
print("Throughput = {} MB/s".format(104.8576/time_taken))

#writing the data to the file
with open("output","wb") as file:
    for data in data_to_written:
        file.write(data)
print("file transfer complete")
