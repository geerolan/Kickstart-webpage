class User():
	def __init__(self, userDoc):
		self.uid = userDoc['_id']
		self.firstName = userDoc['firstName']
		self.lastName = userDoc['lastName']
		self.userName = userDoc['username']
		self.email = userDoc['email']
		self.password = userDoc['password']

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.uid.encode('utf-8')