from flask import Blueprint

api = Blueprint('api', __name__, template_folder='templates')

@api.route("/1", methods=["GET"])
def test1():
    return "ok"