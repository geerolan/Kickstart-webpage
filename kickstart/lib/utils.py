from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class InvalidParamsException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)

class DocNotFoundException(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)

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

def createIdea(col, uName, name, desc, cat, tags):
	ideaDoc = col.IdeaDoc.find_one({"$and": [{"username":uName}, {"name":name}]})
	if ideaDoc:
		raise AlreadyExistsException("Idea %s already exists!" %name)

	dateString = str(datetime.date.today())

	newDoc = col.IdeaDoc()
	newDoc['username'] = uName
	newDoc['name'] = name
	newDoc['normalized'] = name.lower()
	newDoc['desc'] = desc
	newDoc['category'] = cat
	newDoc['created'] = datetime.datetime.today()
	newDoc['tags'] = tags.replace(" ", "").split(",")
	newDoc.save()

def getIdeaById(col, ideaId):
	idea = col.IdeaDoc.find_one({"_id" : ideaId})
	if idea is None:
		raise DocNotFoundException("idea %s not found" %ideaId)
	return idea

def getIdeas(col, sortKey=None):
	if sortKey:
		if sortKey == 'name':
			return col.IdeaDoc.find().sort([("normalized", 1)])
		return col.IdeaDoc.find().sort([("%s" %sortKey, -1)])
	return col.IdeaDoc.find()

def getIdeasByTag(col, tag):
	return col.IdeaDoc.find({"tags" : {"$in": [tag]}})

def deleteIdea(ideaCol, likeCol, ideaId):
	idea = ideaCol.IdeaDoc.find_one({"_id" : ideaId})
	if idea is None:
		raise DocNotFoundException("idea %s not found" %ideaId)
	removeLikes(likeCol, ideaId)
	idea.delete()

def updateIdea(col, ideaId, name, desc, cat, tags):
	idea = getIdeaById(col, ideaId)
	if idea is None:
		raise DocNotFoundException("Idea %s not found" %ideaId)
	idea.name = name
	idea.desc = desc
	idea.category = cat
	rawTags = tags.rstrip(",").replace(" ", "").split(",")
	idea.tags = [raw for raw in rawTags if raw != u""]
	idea.save()

def createLike(col, ideaId, username):
	likeDoc = col.LikeDoc.find_one({"$and": [{"ideaId" : ideaId}, {"username":username}]})
	if likeDoc:
		raise AlreadyExistsException("Idea %s has already been liked by user %s" %(ideaId, username))

	newDoc = col.LikeDoc()
	newDoc['ideaId'] = ideaId
	newDoc['username'] = username
	newDoc.save()

def removeLikes(col, ideaId):
	likeDocs = list(col.LikeDoc.find({"ideaId" : ideaId}))
	print likeDocs

	for likeDoc in likeDocs:
		likeDoc.delete()

def removeLike(col, ideaId, username):
	likeDoc = col.LikeDoc.find_one({"$and": [{"ideaId" : ideaId}, {"username":username}]})
	likeDoc.delete()

def getLiked(col, username):
	return list(col.LikeDoc.find({"username" : username}))

def authenticate(col, uName, pwd):
	userDoc = col.UserDoc.find_one({"username" : uName})
	if userDoc is None:
		raise InvalidLoginException("%s does not exist" %uName)
	if(check_password_hash(userDoc.password, pwd)):
		return userDoc

	raise InvalidLoginException("Invalid username/pwd combination")

def getTopKIdeas(col, k, startDate, endDate):
	#prereq : dates are in form YYYY-MM-DD

	startDate = startDate.split('-')
	endDate = endDate.split('-')
	
	try:
		sDate = datetime.datetime(int(startDate[0]), int(startDate[1]), int(startDate[2]))
		eDate = datetime.datetime(int(endDate[0]), int(endDate[1]), int(endDate[2]))

	except ValueError as e:
		raise InvalidParamsException(str(e))

	return col.IdeaDoc.find({
		"created" : {
		"$gte": sDate,
		"$lt": eDate}
		}).sort([("likes", -1)]).limit(int(k))

def getStats(col):
	cursor = col.aggregate({ "$group" :
			{"_id" : "$category", "total" : {"$sum" : 1}}
		})
	return cursor['result']