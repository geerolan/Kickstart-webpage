from flask import Flask, session, request, redirect, url_for, render_template, make_response
from bson.json_util import dumps, ObjectId
from werkzeug.routing import BaseConverter
from mongokit import Connection
from models.user import UserDoc
from models.idea import IdeaDoc
from models.like import LikeDoc
from lib.utils import *
import datetime
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

@app.route('/')
def index():
	#TODO Add ideas to the template
	if 'username' in session:
		ideas = list(ideaCol.IdeaDoc.find({"username" : session['username']}))
		for idea in ideas:
			idea.created = idea.created.date()
		return render_template('index.html', user=session['username'], ideas=ideas)
	
	return render_template('index.html')

@app.route('/best', methods=['GET'])
def Best():
	if 'username' in session:
		return render_template('topk.html', user=session['username'])
	return render_template('topk.html', user=None)

@app.route('/topk', methods=['GET'])
def TopK():
	if 'k' in request.args:
		try:
			ideas = getTopKIdeas(ideaCol, request.args.get('k'), request.args.get('startDate'), request.args.get('endDate'))
			return dumps(list(ideas))
		
		except InvalidParamsException as e:
			print str(e)
			return make_response(render_template('404.html'), 404)

@app.route('/stats', methods=['GET'])
def showStats():
	categories = ['health', 'technology', 'education', 'finance', 'travel']
	headers = {'Content-Type': 'text/html'}
	stats = getStats(ideaCol)
	if len(stats) > 0:
		rest = [dict([('_id', cat), ('total', 0)]) for cat in categories if next((item for item in stats if item["_id"] == cat), None) is None]
		if len(rest) > 0:
			stats.extend(rest)
		stats = sorted(stats, key=lambda k: k["_id"])

	if 'username' in session:
		return make_response(render_template('stats.html', stats=dumps(stats), user=session['username']), 200, headers)

	return make_response(render_template('stats.html', stats=dumps(stats), user=None), 200, headers)

@app.route('/newIdea', methods=['GET', 'POST'])
def newIdea():
	if 'username' in session:
		if request.method == 'GET':
			return render_template('newIdea.html', user=session['username'])
		try:
			createIdea(ideaCol, request.form['username'], request.form['ideaName'], request.form['desc'], request.form['cat'], request.form['tags'])
			return redirect(url_for('index'))
		except AlreadyExistsException as e:
			return render_template('newIdea.html', msg=str(e))

	return redirect(url_for('index'))

@app.route('/editIdea', methods=['GET', 'POST'])
def editIdea():
	if request.method == 'GET':
		ideaId = ObjectId(request.args.get('ideaId'))
		idea = getIdeaById(ideaCol, ideaId)
		return render_template('editIdea.html', idea=idea, user=session['username'])

	if 'delete' in request.form:
		deleteIdea(ideaCol, likeCol, ObjectId(request.form['ideaId']))
	else:	
		updateIdea(ideaCol, ObjectId(request.form['ideaId']), request.form['ideaName'], request.form['desc'], request.form['cat'], request.form['tags'])
	
	return redirect(url_for('index'))


@app.route('/addLike', methods=['POST'])
def addLike():
	#add new like and increase Like counter on target idea 
	createLike(likeCol,ObjectId(request.form['ideaId']), request.form['username'])
	idea = ideaCol.IdeaDoc.find_one({"_id" : ObjectId(request.form['ideaId'])})
	idea.likes += 1
	idea.save()
	return str(idea.likes)

@app.route('/disLike', methods=['POST'])
def dislike():
	#remove like and decrease Like counter on target idea
	removeLike(likeCol, ObjectId(request.form['ideaId']), request.form['username'])
	idea = ideaCol.IdeaDoc.find_one({"_id" : ObjectId(request.form['ideaId'])})
	idea.likes -= 1
	idea.save()
	return str(idea.likes)

@app.route('/getLikes', methods=['GET'])
def getLikes():
	idea = ideaCol.IdeaDoc.find_one({"_id" : ObjectId(request.form['ideaId'])})
	return str(idea.likes)

@app.route('/userLiked', methods=['GET'])
def getUserLike():
	like = likeCol.LikeDoc.find_one({"$and": [{"username": request.args.get('username')}, {"ideaId": ObjectId(request.args.get('ideaId'))}]})
	print like
	if like is not None:
		return "y"
	return "n"

@app.route('/browse', methods=['GET'])
def browseIdeas():
	if 'tag' in request.args:
		ideas = list(getIdeasByTag(ideaCol, request.args.get('tag')))
	elif 'cat' in request.args:
		ideas = list(getIdeasByCategory(ideaCol, request.args.get('cat')))
	else:
		ideas = list(getIdeas(ideaCol, "name"))

	for idea in ideas:
		#created date is currently in form of datetime.datetime, need to
		#convert to datetime.date ie yyyy-mm-dd
		idea['created'] = idea['created'].date()

	if 'username' in session :
		return render_template('browse.html', ideas=ideas, user=session['username'])

	return render_template('browse.html', ideas=ideas)

@app.route('/ideas/<regex("\w+"):ideaId>', methods=['GET'])
def displayIdea(ideaId):
	idea = getIdeaById(ideaCol, ObjectId(ideaId))
	if idea is not None:
		if 'username' in session:
			return render_template('idea.html', idea=idea, user=session['username'])
		return render_template('idea.html', idea=idea, user=None)

	return render_template('404.html')

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
