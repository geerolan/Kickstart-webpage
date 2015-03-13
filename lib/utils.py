from werkzeug.security import generate_password_hash

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