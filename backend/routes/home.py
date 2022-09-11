from flask import jsonify, request, redirect, url_for, render_template
from flask import Blueprint
home = Blueprint('home', __name__)

from backend.models import User

@home.route('/')
def home_handler():
    return 'Hi Flask App ! '


@home.route('/users', methods=['GET'])
def read_all_users_handler():
    all_users = User.query.all()
    user_list = []
    
    for user in all_users:
        print(user.__dict__)
        print(type(user.__dict__))

        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state', None)
        user_list.append(user_dict)
    
    # import json
    # return json.dumps(user_list)
    return jsonify(user_list)


@home.route('/go_get_referrer', methods=['GET', 'POST'])
def go_get_referrer_handler():
    if request.method == 'POST':
        if request.form['submit_button'] == 'go to get referrer page':
            return redirect(url_for('home.get_referrer_handler'))
    return render_template("go_get_referrer.html")


@home.route('/get_referrer', methods=['GET'])
def get_referrer_handler():
    print(request.referrer)
    print(type(request.referrer))
    return jsonify(request.referrer)


@home.route('/get_post', methods=['GET', 'POST'])
def get_post_handler():
    if request.method == 'POST':
        print(request.get_json())
        print(type(request.get_json()))
    return request.data
