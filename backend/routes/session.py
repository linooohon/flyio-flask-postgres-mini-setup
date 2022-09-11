import flask
from flask import jsonify, request, redirect, url_for, render_template
from flask import Blueprint
session = Blueprint('session', __name__)

from backend.models import User

@session.route('/set_session', methods=['GET'])
def set_session_handler():
    flask.session['user1'] = {
        'name': 'ben',
        'phone': '0800'
    }
    return jsonify(flask.session['user1'])


@session.route('/get_session', methods=['GET'])
def get_session_handler():
    return jsonify(flask.session['user1'])

