from mongokit import Document

class IdeaDoc(Document):
	structure = {
		'username': basestring,
		'name': basestring,
		'desc': basestring,
		'tags': [basestring],
		'likes' : int
	}
 
	default_values = {'likes' : 0}

	use_dot_notation = True
