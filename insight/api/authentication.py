from flask.ext.httpauth import HTTPBasicAuth
from ..models import User
from flask import g
#from ..insight import app
from flask import current_app

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token,password):
	user = User.verify_auth_token(current_app.config["SECRET_KEY"])	
	if not user:
		#try to authenticate with username/password
		user = User.query.filter_by(username=username_or_token).first()
		if not user or not user.verify_password(password):
			return False
	g.user = user
	return True


