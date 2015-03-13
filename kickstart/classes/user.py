class User(userDoc):
	uid = userDoc._id.encode('utf-8')
	firstName = userDoc.firstName
	lastName = userDoc.lastName
	userName = userDoc.userName
	email = userDoc.email
	password = userDoc.password

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.uid