from mongokit import Document, ObjectId

class LikeDoc(Document):
	structure = {
		'ideaId': ObjectId(),
		'username': basestring
	}
 
	use_dot_notation = True