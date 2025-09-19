
class BaseComponent:
	name: str

	def register(self, server, config=None):
		"""Hook into the server lifecycle"""
		raise NotImplementedError
