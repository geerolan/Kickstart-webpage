from flask import Flask, request, render_template
from mongokit import Connection
from models.user import UserDoc

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection(app.config['MONGODB_HOST'], 
						app.config['MONGODB_PORT'])

connection.register([UserDoc])
userCol = connection['dev'].users

#Login manager
def init_login():
	login_manager = LoginManager()
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(uid):
		return utils.getUser(uid)

@app.route('/')
def index():
	return render_template('index.html')

#Initialize flask-login
init_login()

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		User = utils.authenticate(request.data['username'], request.data['pwd'])
		if User is not None:
			login.login_user(User)
			if login.current_user.is_authenticated():
				redirect(url_for('index'), isAuth='true')
			redirect(url_for('index'), isAuth='true')
		else
			redirect(url_for('index'), isAuth='false')
	else:
		render_template('login.html', isAuth='false')	

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		uName = request.data['username']
		fName = request.data['firstName']
		lName = request.data['lastName']
		pwd = request.data['pwd']
		utils.createUser(userCol, uName, fName, lName, pwd)
		return redirect(url_for('/login'))

	else:
		return render_template('register.html')

if __name__ == '__main__':
	app.run()
