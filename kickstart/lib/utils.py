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
	
	newDoc.save()

def createIdea(col, uName, name, desc):
	ideaDoc = col.IdeaDoc.find_one({"$and": [{"username":uName}, {"name":name}]})
	if ideaDoc:
		raise AlreadyExistsException("Idea %s already exists!" %name)

	newDoc = col.IdeaDoc()
	newDoc['username'] = uName
	newDoc['name'] = name
	newDoc['desc'] = desc
	newDoc.save()

def getAllIdeas(col):
	return col.IdeaDoc.find()

def updateIdea(col, ideaId, name, desc):
	idea = col.IdeaDoc.find_one({"_id" : ideaId})
	idea.name = name
	idea.desc = desc
	idea.save()

def createLike(col, ideaId, username):
	likeDoc = col.LikeDoc.find_one({"$and": [{"ideaId" : ideaId}, {"username":username}]})
	if likeDoc:
		raise AlreadyExistsException("Idea %s has already been liked by user %s" %(ideaId, username))

	newDoc = col.LikeDoc()
	newDoc['ideaId'] = ideaId
	newDoc['username'] = username
	newDoc.save()

def removeLike(col, ideaId, username):
	likeDoc = col.LikeDoc.find_one({"$and": [{"ideaId" : ideaId}, {"username":username}]})
	likeDoc.delete()

def getLiked(col, username):
	return list(col.LikeDoc.find({"username" : username}))

def authenticate(col, uName, pwd):
	userDoc = col.UserDoc.find_one({"username" : uName})
	if userDoc is None:
		raise InvalidLoginException("User does not exist")
	if(check_password_hash(userDoc.password, pwd)):
		return userDoc

	raise InvalidLoginException("Invalid username/pwd combination")

