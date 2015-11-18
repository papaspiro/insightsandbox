from datetime import datetime
from flask import render_template,session,redirect,url_for
from . import main
from .. import db
from ..models import Election

@main.route('/',methods=['GET','POST'])
def index():
	e = Election.query.get(1)
	e2000 = {'iteration':e.iteration,'election_year':e.election_year,'electiontype':e.electiontype}
	return render_template('main/index.html',name=session.get('name'),e=e2000)