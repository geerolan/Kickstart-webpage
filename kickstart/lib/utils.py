from werkzeug.security import generate_password_hash, check_password_hash

class InvalidLoginException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)

class AlreadyExistsException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)

def createUser(col, uName, fName, lName, email, pwd):
	userDoc = col.UserDoc.find_one({"username" : uName})
	if userDoc:
		raise AlreadyExistsException("user %s already exists" %uName)

	newDoc = col.UserDoc()
	newDoc['username'] = uName
	newDoc['firstName'] = fName
	newDoc['lastName'] = lName
	newDoc['email'] = email
	newDoc['password'] = generate_password_hash(pwd)
	
	try:
		newDoc.validate()
		newDoc.save()
	except Exception:
		raise Exception

def authenticate(col, uName, pwd):
	userDoc = col.UserDoc.find_one({"username" : uName})
	if(userDoc is not None and check_password_hash(userDoc.password, pwd)):
		return userDoc

	raise InvalidLoginException("Invalid username/pwd combination")

