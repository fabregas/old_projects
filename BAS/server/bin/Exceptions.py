
class Error(Exception):
	def __init__(self, msg):
		self.message = "[BAS ERROR]%s" % msg

	def __str__(self):
		return self.message

	def __repr__(self):
		return self.message
