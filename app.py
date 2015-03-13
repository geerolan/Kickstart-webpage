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

@app.route('/login', methods=['GET', 'POST'])
def login():
	#TODO insert dat body 

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



