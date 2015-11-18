from  insight.api.views import *

from . import api

api.add_resource(ElectionListResource, '/api/v1.0/elections/', endpoint = 'elections')
api.add_resource(ElectionResource, '/api/v1.0/elections/<int:id>', endpoint = 'election')

api.add_resource(CandidateListResource, '/api/v1.0/candidates/', endpoint = 'candidates')
api.add_resource(CandidateResource, '/api/v1.0/candidates/<int:id>', endpoint = 'candidate')
api.add_resource(UserResource, '/api/v1.0/users/', endpoint = 'users')
api.add_resource(AuthenticationResource,'/api/v1.0/token',endpoint='token')

