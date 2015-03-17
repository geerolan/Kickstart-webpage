from flask import Flask, session, request, redirect, url_for, render_template
from mongokit import Connection
from models.user import UserDoc
from models.idea import IdeaDoc
from lib import utils

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection(app.config['MONGODB_HOST'], 
						app.config['MONGODB_PORT'])

connection.register([UserDoc, IdeaDoc])
userCol = connection['dev'].users
ideaCol = connection['dev'].ideas

app.secret_key = 'zK\x88\xb8)\x07\x00\xb4\xab\x08Dw\xc1L\x96\t\xddiZ7\xba\xe2\xc8\x07'

@app.route('/')
def index():
	#TODO Add ideas to the template
	if 'username' in session:
		ideas = ideaCol.IdeaDoc.find({"username" : session['username']})
		return render_template('index.html', loggedIn="true", user=session['username'], ideas=ideas)
	
	return render_template('index.html', loggedIn="false")


@app.route('/editIdea', methods=['GET', 'POST'])
def editIdea():
	if request.method == 'GET':
		print 'should not be here'
		ideaId = request.args.get('ideaId')
		if ideaId:
			#idea exists, open up edit form
			idea = ideaCol.IdeaDoc.find_one({"_id" : ideaId})
			return render_template('editIdea.html', idea=idea)
		return render_template('editIdea.html', idea=None, username=request.args.get('username'))

	if request.method == 'POST':
		print request.form['ideaId']
		if request.form['ideaId'] != '0':
			#update idea
			utils.updateIdea(ideaCol, request.form['ideaId'], request.form['ideaName'], request.form['desc'])
			return redirect(url_for('index'))

		try:
			utils.createIdea(ideaCol, request.form['username'], request.form['ideaName'], request.form['desc'])
		except AlreadyExistsException as e:
			return render_template('/editIdea', msg=str(e))

		return redirect(url_for('index'))

@app.route('/browse', methods=['GET'])
def browseIdeas():
	ideas = utils.getAllIdeas(ideaCol)
	#TODO convert mongodb cursor to list of ideas
	return render_template('browse.html', ideas=ideas)

@app.route('/login', methods=['POST'])
def login():
	try:
		User = utils.authenticate(userCol, request.form['username'], request.form['pwd'])
		session['username'] = User.username
		return redirect(url_for('index'))

	except utils.InvalidLoginException as e:
		return render_template('index.html', loggedIn='false', msg=str(e))

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		uName = request.form['username']
		fName = request.form['firstName']
		lName = request.form['lastName']
		email = request.form['email']
		pwd = request.form['pwd']
		try:
			utils.createUser(userCol, uName, fName, lName, email, pwd)
			return redirect(url_for('/'))
		except utils.AlreadyExistsException as e:
			return render_template('register.html', msg=str(e))

	return render_template('register.html')

if __name__ == '__main__':
	app.run(debug=True)
