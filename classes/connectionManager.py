

class connectionManager():
	"""
		Class that handles all of the open connections for each shell
	"""

	def __init__(self):
		self.shell_ids = Set()#shells need to be a tuple of id,connection
		self.connection_list = []
		
	def add_shell(self,shell_id):
		if shell_id in shell_ids:
			pass
			#no need to spawn new connection because there already exists one
		else:
			shell_ids.add(shell_id)
