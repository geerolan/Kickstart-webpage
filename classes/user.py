class User:
	def __init__(self, id):
		self.is_authenticated = False
		self.is_active = False
		self.is_anonymous = False
		self.id = id

	def get_id(self):
		return unicode(self.id, "utf-8")
