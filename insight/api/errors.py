from . import api
from .. import main
#@main.errorhandler(404)
def  page_not_found(e):
	if request.accept_mimetypes.accept_json	 and not request.accept_mimetypes.accept_html:
		response = jsonify({'error':'not found'})
		response.status_code = 404
		return response
	return render_template('api/404.html'), 404

#@api.errorhandler(500)
def internal_server_error(e):
	return render_template('api/500.html'),500
	
