from flask import Flask, session, request, redirect, url_for, render_template
from flask.ext.restful import Api, Resource, abort
from bson.objectid import ObjectId
from bson.json_util import dumps
from werkzeug.routing import BaseConverter
from mongokit import Connection
from models.user import UserDoc
from models.idea import IdeaDoc
from models.like import LikeDoc
from lib.utils import *

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

class RegexConverter(BaseConverter):
	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]

app = Flask(__name__)
app.config.from_object(__name__)
app.url_map.converters['regex'] = RegexConverter

connection = Connection(app.config['MONGODB_HOST'], 
						app.config['MONGODB_PORT'])

connection.register([UserDoc, IdeaDoc, LikeDoc])
userCol = connection['dev'].users
ideaCol = connection['dev'].ideas
likeCol = connection['dev'].likes

app.secret_key = 'zK\x88\xb8)\x07\x00\xb4\xab\x08Dw\xc1L\x96\t\xddiZ7\xba\xe2\xc8\x07'

#Restful interface
api = Api(app)
class TopK(Resource):
	def get(self, k, startDate, endDate):
		headers = {'Content-Type': 'text/html'}
		try:
			#note, if none are found, returns "[]"
			ideas = dumps(getTopKIdeas(ideaCol, k, startDate, endDate))
			
			return make_response(render_template('topk.html', ideas=ideas), 200, headers)

		except InvalidParamsException as e:
			abort(404, message=str(e))

api.add_resource(TopK, '/best/<regex("\d{4}-\d{2}-\d{2}"):startDate>/<regex("\d{4}-\d{2}-\d{2}"):endDate>/<regex("\d+"):k>')
@app.route('/')
def index():
	#TODO Add ideas to the template
	if 'username' in session:
		ideas = list(ideaCol.IdeaDoc.find({"username" : session['username']}))
		return render_template('index.html', user=session['username'], ideas=ideas)
	
	return render_template('index.html')


@app.route('/editIdea', methods=['GET', 'POST'])
def editIdea():
	if 'username' in session:
		if request.method == 'GET':
			if 'ideaId' in request.args:
				ideaId = ObjectId(request.args.get('ideaId'))
				print ideaId
				idea = getIdeaById(ideaCol, ideaId)
				return render_template('editIdea.html', idea=idea, user=session['username'])
			return render_template('editIdea.html', idea=None, user=session['username'])

		if request.method == 'POST':
			if request.form['ideaId'] != '0':
				updateIdea(ideaCol, ObjectId(request.form['ideaId']), request.form['ideaName'], request.form['desc'], request.form['tags'])
				return redirect(url_for('index'))
			try:
				print request.form
				createIdea(ideaCol, request.form['username'], request.form['ideaName'], request.form['desc'], request.form['cat'], request.form['tags'])
				return redirect(url_for('index'))
			except AlreadyExistsException as e:
				return render_template('editIdea.html', msg=str(e))

	return redirect(url_for('index'))

@app.route('/addLike', methods=['POST'])
def addLike():
	#add new like and increase Like counter on target idea 
	createLike(request.form['ideaId'], request.form['username'])
	idea = ideaCol.IdeaDoc.find_one({"_id" : ideaId})
	idea.likes += 1
	idea.save()

@app.route('/dislike', methods=['POST'])
def dislike():
	#remove like and decrease Like counter on target idea
	removeLike(likeCol, request.form['ideaId'], request.form['username'])
	idea = ideaCol.IdeaDoc.find_one({"_id" : ideaId})
	idea.likes -= 1
	idea.save()

@app.route('/browse', methods=['GET'])
def browseIdeas():
	ideas = list(getAllIdeas(ideaCol))
	if 'username' in session :
		return render_template('browse.html', ideas=ideas, user=session['username'])

	return render_template('browse.html', ideas=ideas)

@app.route('/ideas/<regex("\w+"):ideaId>', methods=['GET'])
def displayIdea(ideaId):
	idea = getIdeaById(ideaCol, ObjectId(ideaId))
	#if none, then redirect to a 404
	return render_template('idea.html', idea=idea)

@app.route('/login', methods=['POST'])
def login():
	try:
		User = authenticate(userCol, request.form['username'], request.form['pwd'])
		session['username'] = User.username
		return redirect(url_for('index'))

	except InvalidLoginException as e:
		return render_template('index.html', msg=str(e))

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		try:
			createUser(userCol, request.form['username'], request.form['firstName'], request.form['lastName'], request.form['email'], request.form['pwd'])
			return redirect(url_for('index'))
		except AlreadyExistsException as e:
			return render_template('register.html', msg=str(e))

	return render_template('register.html')

if __name__ == '__main__':
	app.run(debug=True)
