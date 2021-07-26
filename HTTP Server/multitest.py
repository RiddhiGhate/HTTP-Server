import socket
import sys
import threading
import time
import errno
import requests


SOCKET_AMOUNT = 50
HOST, PORT = '127.0.0.1', 1300

def client(ip, port, req):
	try:
		parts = req.decode().split(' ')
		URL = 'http://127.0.0.1:1300/{}'.format(parts[1])
		#HEADERS = {'If-Modified-Since':'Thursday,2020-11-11 15:04:05.541974'}
		if parts[0] == 'GET':
			r = requests.get(url = URL)
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)
			with open(parts[1], 'wb+') as f:
				f.write(r.content)
		
		elif parts[0] == 'OPTIONS':
			r = requests.options(url = URL)
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)
		
		elif parts[0] == 'POST':
			name = input("Enter a value(your name) : ")
			file = input("Enter file name in the same directory : ")
			with open(file, 'rb') as f:
				filedata = f.read()
			multipart_form_data = {'fileToUpload' : (name,filedata), 'name' : (None,name)}
			r = requests.post(url = URL, files = multipart_form_data)
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)
		
		elif parts[0] == 'PUT':
			file = input("Enter file name in the same directory : ")
			with open(file, 'rb') as f:
				filedata = f.read()
			r = requests.put(url = URL, files = {'fileToUpload' : (file,filedata)})
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)
		
		elif parts[0] == 'HEAD':
			r = requests.head(url = URL)
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)
		
		elif parts[0] == 'delete'.upper():
			r = requests.delete(url = URL)	
			print(r.status_code)
			for k, v in r.headers.items():
				print('{} : {}'.format(k,v))
			print(r.content)		
		
			
	except IOError as e:
		if e.errno == errno.EPIPE:
			print("oops")
	except ConnectionResetError:
		print("connection error")



for i in range(SOCKET_AMOUNT):
	req = input()
	client_thread = threading.Thread(target=client, args=(HOST, PORT, req.encode()))
	client_thread.start()


	
	
	