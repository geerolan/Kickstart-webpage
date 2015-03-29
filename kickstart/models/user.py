from mongokit import Document

class UserDoc(Document):
	structure = {
		'username': basestring,
		'firstName': basestring,
		'lastName': basestring,
		'email' : basestring,
		'password': basestring
	}

	use_dot_notation = True

