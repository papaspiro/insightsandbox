from flask import Blueprint
from ..models import Election

main = Blueprint('main',__name__)


from . import views,errors