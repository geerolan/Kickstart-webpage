from mongokit import Document, Connection

class UserDoc(Document):
	structure = {
		'username': basestring,
		'firstName': basestring,
		'lastName': basestring,
		'password': basestring
	}

	required_fields = ['username', 'firstName', 'lastName', 'password']

	use_dot_notation = True

