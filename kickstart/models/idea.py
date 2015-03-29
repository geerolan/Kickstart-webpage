from mongokit import Document
import datetime

class IdeaDoc(Document):
	structure = {
		'username': basestring,
		'name': basestring,
		'normalized': basestring,
		'desc': basestring,
		'category': basestring,
		'created': datetime.datetime,
		'tags': [basestring],
		'likes' : int
	}
 
	default_values = {'likes' : 0}

	use_dot_notation = True
