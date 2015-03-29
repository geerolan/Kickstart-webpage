from mongokit import Document
class LikeDoc(Document):
	structure = {
		'ideaId': None,
		'username': basestring
	}
 
	use_dot_notation = True