#!/usr/bin/python
from socket import *
import sys

serversocket = socket(AF_INET, SOCK_STREAM)
serverport = int(sys.argv[1])
serversocket.bind(('', serverport))
serversocket.listen(1)
print("The server is ready to receive")
while True:
	connectionsocket, addr = serversocket.accept()
	print("New request received from");print(addr);
	print("Connection socket is");print(connectionsocket);
	request = connectionsocket.recv(1024).decode()
	
	parts = request.split()
	print(parts[0], parts[1])
	if(parts[0] == "GET"):
		
		string = " 200 OK\n"
		string += "Access-Control-Allow-Origin: *\n"
		string += "Content-Encoding: gzip\n"
		string += "Transfer-Encoding: chunked\n"
		#string += "Content-Type: " + str(mimetypes.guess_type(filename[1])) +"\n"
		#string += "Date: " + str(datetime.datetime.today().strftime('%A')) + ", " + str(datetime.datetime.now(pytz.timezone('Asia/Kolkata'))) +"\n"
		#string += "Last-Modified: " + str(datetime.datetime.fromtimestamp(t)) +"\n"
		string += "Server: Riddhi's Server/0.0.1 (Ubuntu)\n"
		string += "Set-Cookie: mykey=myvalue; expires=Mon, 17-Jul-2017 16:06:00 GMT; Max-Age=31449600; Path=/; secure\n"
		#string += "Content-Length:" + str(file_stats.st_size) +"\n"
		string += "Connection: close\n\n"
		f = open("photo.png", 'rb')
		text = f.read()
	
		#Mon, 18 Jul 2016 02:36:04 GMT
		response = string + text
		connectionsocket.send(response.encode())
				
	connectionsocket.close()

