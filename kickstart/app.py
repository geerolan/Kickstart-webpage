from flask import Flask, session, request, redirect, url_for, render_template
from mongokit import Connection
from models.user import UserDoc
from lib import utils

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection(app.config['MONGODB_HOST'], 
						app.config['MONGODB_PORT'])

connection.register([UserDoc])
userCol = connection['dev'].users

app.secret_key = 'zK\x88\xb8)\x07\x00\xb4\xab\x08Dw\xc1L\x96\t\xddiZ7\xba\xe2\xc8\x07'

@app.route('/')
def index():
	if 'username' in session:
		return render_template('index.html', loggedIn="true")
	print "not in session"
	return render_template('index.html', loggedIn="false")


@app.route('/login', methods=['POST'])
def login():
	try:
		User = utils.authenticate(userCol, request.form['username'], request.form['pwd'])
		session['username'] = User.username
		return redirect(url_for('index'))

	except utils.InvalidLoginException as e:
		return render_template('index.html', loggedIn='false', msg=str(e))

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
