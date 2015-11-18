from flask_restful import Resource, Api,reqparse
from flask_restful import fields,marshal	
from flask import jsonify
from flask import url_for
from ..models import *
from .. import db
from flask import abort

from . import api
from authentication import auth

import datetime

from sqlalchemy import func
from flask import g

#from flask.ext.httpauth import HTTPBasicAuth

#auth = HTTPBasicAuth()

election_type_fields= {
	'id':fields.Integer,
	'type': fields.String
}

iteration_fields ={
	'id': fields.Integer,
	'description': fields.String
}




election_fields ={

		'electiontype':fields.String,
		'election_year' :fields.DateTime(dt_format='iso8601'),
		'iteration' :fields.String,
		'uri':fields.Url('.election')
	}

eccv_fields ={
	''
}

#candidate_election{}

candidate_fields ={

	'first_name':fields.String,
	'last_name': fields.String,
	'uri' :fields.Url('.candidate',absolute=True)
	#'elections' : fields.Nested(election_fields)
}

class AuthenticationResource(Resource):
	decorators=[auth.login_required]  	
	def get(self):
		#user = User.query.get(1)
		#if g.user is not  None:
		token = g.user.generate_auth_token()
		return jsonify({"token": token.decode("ascii")})		
		#return None
	


class ElectionListResource(Resource):

	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('election_year',type=str,required=True,
			help='election year is required',location="json")
		self.reqparse.add_argument('iteration',type=str,required=True,
			help='Iteration argument missing',location='json')
		super(ElectionListResource,self).__init__()

	def get(self):
		e = Election.query.all()
		return marshal(e,election_fields)



	def post(self):
		pass

	def delete(self):
		pass		

class ElectionResource(Resource):
	decorators=[auth.login_required]
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument("iteration",type=str,location="json")
		self.reqparse.add_argument("election_year",type=datetime.date,location="json")
		self.reqparse.add_argument("election_type",type=str,location="json")
		super(ElectionResource,self).__init__()

	
	def get(self,id):
		e = Election.query.get(id)

		if e is None:
			abort(404)

		el_cands = ElectionCandidate.query.filter(ElectionCandidate.election_id.in_([id])).all()
		ec = [ el_cand.candidate for el_cand in el_cands]
	
		ec_ids = [ el_cand.id for el_cand in el_cands]
		
		#candidate votes
		ec_votes= db.session.query(func.sum(ElectionCandidateConstituencyVote.votes
		),ElectionCandidateConstituencyVote.election_candidate_id).filter(
		ElectionCandidateConstituencyVote.election_candidate_id.in_(ec_ids)).group_by(
		ElectionCandidateConstituencyVote.election_candidate_id).order_by(
		ElectionCandidateConstituencyVote.votes).all()


		ec_votes_fields= [ 
			[
			   marshal( ElectionCandidate.query.get( ec_vote[1] ).candidate , candidate_fields),
			   ec_vote[0]
			]

			for ec_vote in ec_votes
		]
		
		#'candidates': marshal(ec,candidate_fields,
			
		#e_constituency_result''
		return { 'election': marshal(e,election_fields),'candidate_votes': ec_votes_fields }


	def post(self):
		pass

	def put(self):
		pass




class CandidateListResource(Resource):

	def get(self):
		c = Candidate.query.all()		

		return {'candidates':marshal(c,candidate_fields)}

	def put(self,id):
		pass

	def delete(self,id):
		pass	

class CandidateResource(Resource):
	decorators = [auth.login_required]

	def get(self,id):
		c = Candidate.query.get(id)

		c.e =  [e.election for e in c.elections]
		candidate = {}
		candidate['bio'] = c
		candidate['elections'] = c.elections

		return {'candidate':marshal(c,candidate_fields),'elections' :marshal(c.e,election_fields) }

	def put(self,id):
		pass

	def delete(self,id):
		pass	


class UserResource(Resource):

	def __init__(self):

		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('username',type=str,required=True,
			help='username is required',location="json")
		self.reqparse.add_argument('password',type=str,required=True,
			help='passord missing',location='json')
		
		super(UserResource,self).__init__()

	def get(self,id):
		user = User.query.get(id)
		if not user:
			abort(400)
		return jsonify({'username':user.username})


	def post(self):
		args = self.reqparse.parse_args()		
		username = args['username']
		password = args['password']
		
		if username is None or password is None	:
			abort(400)

		user = User(username=username)
		user.hash_password(password)
		db.session.add(user)
		db.session.commit()

		return jsonify({'username':user.username })




		
#api.add_resource(ElectionListResource, '/api/v1.0/elections', endpoint = 'elections')
#api.add_resource(CandidateListResource, '/api/v1.0/candidates', endpoint = 'candidates')
#api.add_resource(CandidateTestListResource, '/api/v1.0/candidatest', endpoint = 'candidates')
