from werkzeug.security import generate_password_hash, check_password_hash
from classes.user import User

def createUser(col, uName, fName, lName, pwd):
	newDoc = col.UserDoc()
	newDoc['username'] = uName
	newDoc['firstName'] = fName
	newDoc['lastName'] = lName
	newDoc['password'] = generate_password_hash(pwd)
	
	try:
		newDoc.validate()
		newDoc.save()
	except Exception:
		raise Exception

def getUser(col, uid):
	userDoc = col.findOne({"_id" : uid})
	if(userDoc is None):
		return None
	return User(userDoc)
	
def authenticate(col, uName, pwd):
	userDoc = col.findOne({"username" : uName})
	if(userDoc is None):
		return None
	if(check_password_hash(userDoc.password, pwd)):
		return User(userDoc)
	
	return None

