

class connectionManager():
	"""
		Class that handles all of the open connections for each shell
	"""

	def __init__(self):
		self.shell_ids = Set()#shell_ids is just a set of all the shell ids
		self.connection_list = []
		
	def add_shell(self,shell_id):
		if not shell_id in shell_ids:#no connection so add one
			shell_ids.add(shell_id)
			connection_list.append(connection(shell_id))

	def get_connection_by_id(self,shell_id):
		"""
			Returns a connection object based off of the shell id of that connection

			@param shell_id the id of the shell to be retrieved
		"""
		for connect in connection_list:
			if connect.shell_id = shell_id:
				return connect