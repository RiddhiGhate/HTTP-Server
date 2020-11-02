from socket import *
import sys
from select import *
import binascii

servername = '127.0.0.1'
serverport = int(sys.argv[1])
clientsocket = socket(AF_INET, SOCK_STREAM)
clientsocket.connect((servername, serverport))


while True:
	sockets = [sys.stdin, clientsocket]
	read_socket, write_socket, error_socket = select(sockets,[],[])
	for item in read_socket:
		if item == clientsocket:
			incoming = item.recv(65536).decode()
			print (incoming)
   
		else:
			response = input()
			input_req = response.encode()
			clientsocket.send(input_req)
			



