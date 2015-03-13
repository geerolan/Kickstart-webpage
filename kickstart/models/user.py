from mongokit import Document, Connection

class UserDoc(Document):
	structure = {
		'username': basestring,
		'firstName': basestring,
		'lastName': basestring,
		'email' : basestring,
		'password': basestring
	}

	required_fields = ['username', 'firstName', 'lastName', 'email','password']

	use_dot_notation = True

