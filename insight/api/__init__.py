from flask import Blueprint
from flask import Flask, Blueprint
from flask_restful import Api, Resource, url_for

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

#from ..models import Candidate as Candidate 

from . import views, errors,app ,resources, authentication


#from insight.api.resources.candidate import CandidateTestResource