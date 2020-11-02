#!/usr/bin/python
from socket import *
import sys
import threading
import datetime
import pytz
import os
import mimetypes
from random import randint
import re

clients_connected = []
cookie_jar = {}

def normalize_line_endings(s):

	return ''.join((line + '\n') for line in s.splitlines())

def generate_cookie_id(addr):
	cookie_id = ''
	for a in range(0, 9):
		aux = randint(0,9999)
		if not aux % 2:
			for i in range(1, 4):
				letter = randint(97, 123)
				if letter % 2:
					cookie_id += chr(letter)
				else:
					cookie_id += str(letter) + chr(letter)
		cookie_id += str(aux)
	cookie_jar['name'] = addr
	cookie_jar['id'] = cookie_id
	return cookie_id

def parse_urlencoded(request_body):
	modified_body = re.split('&|=', request_body)
	splitted_body = [x.replace('\n','' ) for x in modified_body]
	return splitted_body


def my_thread(connectionsocket, addr):
	while True:
		reqst = connectionsocket.recv(1024000000)
		request = reqst.decode()
		
		if request:
			splitted_request = normalize_line_endings(request) # hack again
			request_head, request_body = splitted_request.split('\n\n',1)
			request_head = request_head.splitlines()
			request_headline = request_head[0]
			print(request_headline)
			print(request_body)
			parts = request_headline.split()
			filename = parts[1].split('/')
			if(parts[0] == "GET"):
				f = open(filename[1], 'rb')
				text = f.read()
				file_stats = os.stat(filename[1])
				t = os.path.getmtime(filename[1])
				cookie_value_returned = generate_cookie_id(addr)
				#connectionsocket.send('Content-Encoding: gzip\n'.encode('utf-8'))
				#connectionsocket.send('Transfer-Encoding: chunked\n\n'.encode('utf-8'))
				#connectionsocket.send("Set-Cookie: mykey=myvalue; expires=Mon, 17-Jul-2017 16:06:00 GMT; Max-Age=31449600; Path=/; secure\n".encode('utf-8'))
				#Mon, 18 Jul 2016 02:36:04 GMT
				#status in headers
				connectionsocket.send('HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *\nSet-Cookie: {}={}\nContent-Type: {}\nDate:  {},{}\nLast-Modified: {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nContent-Length: {}\nConnection: close\n\n'.format(addr,cookie_value_returned,mimetypes.guess_type(filename[1]),datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata')),datetime.datetime.fromtimestamp(t).strftime('%A'),datetime.datetime.fromtimestamp(t),file_stats.st_size).encode('utf-8'))
	   
				connectionsocket.sendall(text)
				
				
				
			elif(parts[0] == "HEAD"):

				f = open(filename[1], 'rb')
				text = f.read()
				file_stats = os.stat(filename[1])
				
				connectionsocket.send('HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *\nSet-Cookie: {}={}\nContent-Type: {}\nDate:  {},{}\nLast-Modified: {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nContent-Length: {}\nConnection: close\n\n'.format(addr,cookie_value_returned,mimetypes.guess_type(filename[1]),datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata')),datetime.datetime.fromtimestamp(t).strftime('%A'),datetime.datetime.fromtimestamp(t),file_stats.st_size).encode('utf-8'))
	   
			elif(parts[0] == "POST"):
				
				if 'Content-Type: application/x-www-form-urlencoded' in request_head:
					splitted_body_returned = parse_urlencoded(request_body)
					with open("post_data.txt", "a") as f:
						f.write(splitted_body_returned[1])
						f.write(splitted_body_returned[3])
				connectionsocket.send('HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *\nContent-type:text/html\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n<h1>Data Submitted!</h1>'.format(datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
			
			else:
				connectionsocket.send('HTTP/1.1 400')
		#else:
			#response = "Bad request"
			#output = response.encode('utf-8')
			#connectionsocket.send(output)
			
			
	connectionsocket.close()

if (__name__=="__main__"):
	serversocket = socket(AF_INET, SOCK_STREAM)
	serverport = int(sys.argv[1])
	serversocket.bind(('', serverport))
	serversocket.listen(1)
	print("The server is ready to receive")
	while True:
		connectionsocket, addr = serversocket.accept()
		clients_connected.append(connectionsocket)
		print("New request received from");print(addr);
		print("Connection socket is");print(connectionsocket);
		t = threading.Thread(target=my_thread, args=(connectionsocket,addr))
		t.start()

