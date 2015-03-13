from werkzeug.security import generate_password_hash, check_password_hash
from kickstart.classes.user import User

def createUser(col, uName, fName, lName, email, pwd):
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

def getUser(col, uid):
	userDoc = col.UserDoc.find_one({"_id" : uid})
	print userDoc
	if(userDoc is None):
		return None
	return User(userDoc)
	
def authenticate(col, uName, pwd):
	userDoc = col.UserDoc.find_one({"username" : uName})
	if(userDoc is None):
		print 'does not exist'
		return None
	if(check_password_hash(userDoc.password, pwd)):
		print 'it checks out'
		return User(userDoc)
	
	return None

