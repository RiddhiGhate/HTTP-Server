#!/usr/bin/python
from socket import *
import sys
import threading
import datetime
from datetime import date
import pytz
import os
import os.path
import mimetypes
from random import randint
import re
import configparser

clients_connected = []
cookie_jar = {}
error_codes = [400,401,404,405]

config = configparser.ConfigParser()
config.read('config/http.conf')
methods = config['HTTP']['allowedmethods'].split(',')
documentroot = config['HTTP']['documentroot']

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

def split_on_boundary(request_head):
	search = 'boundary'
	result = [element for element in request_head if search in element]
	if len(result) > 0:
		returned_boundary = result[0].split('=')
		return returned_boundary[1]
	return 0 

def post_text_data(empty_list, file_data, filename):
	with open("post_data.txt", "a") as f:
		for x in empty_list:
			f.write(x)
		f.write("\n")
		f.close()
	if len(file_data) > 0:
		with open(filename, 'wb+') as fil:
			fil.write(file_data)

def put_text_data(filename, file_data):
	is_present = os.path.isfile(filename)
	if is_present == True:
		if os.access(filename[1], os.R_OK) == True:
			with open(filename, 'wb') as fil:
				fil.write(file_data)
			return 200, 'OK'
		else:
			return 401, 'Unauthorized'
	else:
		with open(filename, 'wb+') as fil:
			fil.write(file_data)
		return 201, 'Created'

def get_modified_date(request_head):
	search = 'If-Modified-Since'
	result = [element for element in request_head if search in element]
	if result:
		returned_date = result[0].split(':', 1)
		return returned_date[1]
	return 0

def get_date(modified_date):
	replaced = str(modified_date).replace(',',' ')
	result = replaced.split(' ')
	mdate = result[2].split('-')
	time = result[3].split('.')[0]
	return mdate, time

def compare_date(if_modified_date, modified_date):
	if_date, if_time = get_date(if_modified_date)
	mdate, time = get_date(modified_date)
	d0 = date(int(if_date[0]), int(if_date[1]), int(if_date[2]))
	d1 = date(int(mdate[0]), int(mdate[1]), int(mdate[2]))
	FMT = '%H:%M:%S'
	t0 = datetime.datetime.strptime(if_time, FMT)
	t1 = datetime.datetime.strptime(time, FMT)
	delta = d1 - d0
	if(delta.days >= 0 and t0.time() >= t1.time()):
		return 1
	return 0

def get_content_length(request_head):
	search = 'Content-Length' 
	result = [element for element in request_head if search in element]
	if result:
		leng = result[0].split(':', 1)
		return leng[1]
	return 0 


def my_thread(connectionsocket, addr):
	data = b""
	while True:
		reqst = connectionsocket.recv(1024)
		data = data + reqst
		if len(reqst) < 1024:
			break
		#request = reqst.decode()
	pos = data.find(b"\r\n\r\n")
	request = data[:pos].decode()
	request_head = request.splitlines()
	request_body = data[pos+4:]
	

	if request:
		splitted_request = normalize_line_endings(request) 
		request_head = request.splitlines()
		request_headline = request_head[0]
		print(request_headline)
		status_code = 200
		status_message = 'OK'

		access_file = config['HTTP']['access_file']
		error_file = config['HTTP']['error_file']
		parts = request_headline.split()
		
		if len(parts) < 3:
			status_code = 400
			status_message = 'Bad Request'
			connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))

		
		else:
			if parts[0] not in methods:
				status_code = 405
				connectionsocket.send('HTTP/1.1 405 Method Not Allowed\nDate: {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n405 Method Not Allowed'.format(datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
				connectionsocket.close()
			
			if(parts[0] == "GET"):
				
				filename = parts[1].split('/',1)
				if len(filename) == 1:
					filename.append(documentroot)
					print(filename)
				if os.path.isfile(filename[1]):
					if os.access(filename[1], os.R_OK) == False:
						status_code = 401
						status_message = 'Unauthorized'
						connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
					else:
						f = open(filename[1], 'rb')
						text = f.read()
						file_stats = os.stat(filename[1])
						t = os.path.getmtime(filename[1])
						cookie_value_returned = generate_cookie_id(addr)
						if_modified_date = get_modified_date(request_head)
						

						if(if_modified_date != 0):
							result = compare_date(if_modified_date, ' ' + str(datetime.datetime.fromtimestamp(t).strftime('%A') + ',' + str(datetime.datetime.fromtimestamp(t))))
							if(result == 1):
								status_code = 304
						connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nSet-Cookie: {}={}\nContent-Type: {}\nDate:  {},{}\nLast-Modified: {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nContent-Length: {}\nConnection: close\n\n'.format(str(status_code),status_message,addr,cookie_value_returned,mimetypes.guess_type(filename[1]),datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata')),datetime.datetime.fromtimestamp(t).strftime('%A'),datetime.datetime.fromtimestamp(t),file_stats.st_size).encode('utf-8'))			
				else:
					status_code = 404
					status_message = 'File Not Found'
					connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
				if(status_code == 200):
					connectionsocket.sendall(text)
		
			
			
			elif(parts[0] == "HEAD"):

				filename = parts[1].split('/',1)
				if os.path.isfile(filename[1]):
					if os.access(filename[1], os.R_OK) == False:
						status_code = 401
						status_message = 'Unauthorized'
						connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
					else:
						f = open(filename[1], 'rb')
						text = f.read()
						file_stats = os.stat(filename[1])
						t = os.path.getmtime(filename[1])
						cookie_value_returned = generate_cookie_id(addr)
						if_modified_date = get_modified_date(request_head)
						

						if(if_modified_date != 0):
							result = compare_date(if_modified_date, ' ' + str(datetime.datetime.fromtimestamp(t).strftime('%A') + ',' + str(datetime.datetime.fromtimestamp(t))))
							if(result == 1):
								status_code = 304
						connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nSet-Cookie: {}={}\nContent-Type: {}\nDate:  {},{}\nLast-Modified: {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nContent-Length: {}\nConnection: close\n\n'.format(str(status_code),status_message,addr,cookie_value_returned,mimetypes.guess_type(filename[1]),datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata')),datetime.datetime.fromtimestamp(t).strftime('%A'),datetime.datetime.fromtimestamp(t),file_stats.st_size).encode('utf-8'))			
				else:
					status_code = 404
					status_message = 'File Not Found'
					connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
				   
			
			elif(parts[0] == "POST"):
				empty_list = []
				file_data = b''
				file_name = ''
				if 'Content-Type: application/x-www-form-urlencoded' in request_head:
					splitted_body_returned = parse_urlencoded(request_body)
					with open("post_data.txt", "a") as f:
						f.write(splitted_body_returned[1])
						f.write(splitted_body_returned[3])
				else:
					returned_boundary = split_on_boundary(request_head)
					if returned_boundary != 0:
						actual_boundary = '--' + returned_boundary
						body_lines = request_body.split(actual_boundary.encode())
						for x in range (1, len(body_lines) - 1):
							pos = body_lines[x].find(b'filename')
							if(pos != -1): 
								pos1 = body_lines[x].find(b'\r\n\r\n')
								part1 = body_lines[x][:pos1]
								file_data = body_lines[x][pos1+4:]
								filename = part1.decode()
								file_list = filename.split('filename=')
								temp = file_list[1].split('Content-Type')
								file_name = temp[0].split('"')[1]
							else:
								pos = body_lines[x].find(b'\r\n\r\n')
								entity = body_lines[x][pos+4:]
								empty_list.append(entity.decode())
						post_text_data(empty_list, file_data, file_name)
					else:
						status_code = 204
						status_message = 'No Content'

				connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nContent-type:text/html\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n<h1>Data Submitted!</h1>'.format(status_code,status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
			
			elif(parts[0] == "PUT"):
				filename = parts[1].split('/',1)
				returned_boundary = split_on_boundary(request_head)
				if returned_boundary != 0:
					actual_boundary = '--' + returned_boundary
					body_lines = request_body.split(actual_boundary.encode())
					file_data = body_lines[1][pos+4:]
					status_code, status_message = put_text_data(filename[1], file_data)
				else:
					status_code = 204
					status_message = 'No Content'
				connectionsocket.send('HTTP/1.1 {} {}\nAccess-Control-Allow-Origin: *\nContent-type:text/html\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n<h1>Done!</h1>'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))

			elif(parts[0].lower() == "delete"):
				filename = parts[1].split('/',1)
				status_code = 202
				status_message = 'Accepted'
				connectionsocket.send('HTTP/1.1 {} {}\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))
				if os.path.isfile(filename[1]):
					os.remove(filename[1])
					status_code = 200
					status_message = 'OK'
				elif os.path.isdir(filename[1]):
					os.rmdir(filename[1])
					status_code = 200
					status_message = 'OK'
				else:
					status_code = 204
					status_message = 'No Content'

				connectionsocket.send('HTTP/1.1 {} {}\nDate:  {},{}\nServer: Riddhi\'s Server/0.0.1 (Ubuntu)\nConnection: close\n\n'.format(str(status_code),status_message,datetime.datetime.today().strftime('%A'),datetime.datetime.now(pytz.timezone('Asia/Kolkata'))).encode('utf-8'))	


			with open(access_file, 'a') as f:
				f.write(str(addr[0]))
				f.write(' ')
				f.write(str(addr[1]))
				f.write(' ')
				f.write(str(datetime.datetime.today().strftime('%A')))
				f.write(',')
				f.write(str(datetime.datetime.now(pytz.timezone('Asia/Kolkata'))))
				f.write(' ')
				f.write(request_headline)
				f.write(' ')
				f.write(str(status_code))
				f.write('\n')
				f.close()
			
			with open(error_file, 'a') as f:
				if status_code in error_codes:
					f.write(str(addr[0]))
					f.write(' ')
					f.write(str(addr[1]))
					f.write(' ')
					f.write(str(datetime.datetime.today().strftime('%A')))
					f.write(',')
					f.write(str(datetime.datetime.now(pytz.timezone('Asia/Kolkata'))))
					f.write(' ')
					f.write(request_headline)
					f.write(' ')
					f.write(str(status_code))
					f.write('\n')
				f.close()
			

	connectionsocket.close()

if (__name__=="__main__"):
	serversocket = socket(AF_INET, SOCK_STREAM)
	serverport = int(sys.argv[1])
	serversocket.bind(('', serverport))
	serversocket.listen(20)
	print("The server is ready to receive")
	while True:
		connectionsocket, addr = serversocket.accept()
		clients_connected.append(connectionsocket)
		print("New request received from");print(addr);
		print("Connection socket is");print(connectionsocket);
		t = threading.Thread(target=my_thread, args=(connectionsocket,addr))
		t.start()

