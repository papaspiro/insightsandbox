from flask_restful import Resource
#from insight.models import Candidate

from flask import jsonify


class CandidateTestResource(Resource):
	
	def get(self):
		return jsonify({'hello':'Hello World'})

	def put(self):
		pass


	def delete(self):
		pass