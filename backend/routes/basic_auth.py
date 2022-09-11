"""
/basic_auth/login -> @auth.login_required -> @auth.verify_password -> def verify_password(username, password) -> def basic_auth_login_handler()

"""
from email import message
import re
import unicodedata


from flask import jsonify, request
from flask import Blueprint
basic_auth = Blueprint('basic_auth', __name__)
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from werkzeug.security import generate_password_hash, check_password_hash

from backend import db
from backend.models import User


@basic_auth.route('/basic_auth/home', methods=['GET'])
def basic_auth_home_handler():
    return 'Hi Flask App basic auth home! '

@auth.verify_password
def verify_password(username, password):
    exist_user = db.session.query(User).filter_by(user_id=username).first()
    print(exist_user)
    if not exist_user: 
        print('user is not exist')
        return {'message': 'user is not found'}

    # when signup we used `generate_password_hash` to hash plain password with sha256 and save it to db, 
    # now we pick db password and the password user is giving to confirm if it is the same.
    # if same then we let them login.
    if check_password_hash(exist_user.password, password):
        print('user is exist and pass')
        return True
    else:
        print('user is exist but not pass')
        return {'message': 'authentication failed'}

@basic_auth.route('/basic_auth/login', methods=['GET'])
@auth.login_required
def basic_auth_login_handler():
    if request.method == 'GET':
        return basic_auth_login_handler_get()

@basic_auth.route('/basic_auth/reset', methods=['PATCH'])
@auth.login_required
def basic_auth_reset_handler():
    if request.method == 'PATCH':
        return basic_auth_reset_handler_patch()


@basic_auth.route('/basic_auth/delete', methods=['POST'])
@auth.login_required
def basic_auth_delete_handler():
    if request.method == 'POST':
        if 'message' in auth.current_user() and type(auth.current_user()) == dict:
            if auth.current_user()['message'] == 'user is not found': return jsonify({'message': 'user is not found'}), 404
            if auth.current_user()['message'] == 'authentication failed': return jsonify({'message': 'authentication failed'}), 401
        if 'message' not in auth.current_user() and type(auth.current_user()) != dict:
            success, message = delete_user_in_db(auth.current_user())
            if success:
                return message, 200
            else:
                return message, 400

        


"""

```
curl --location --request GET 'http://127.0.0.1:5000/basic_auth/login' \
--header 'Authorization: Basic VG9tMTIzNDpAVG9tMTIzNA=='
```

```
If ----> ex: username: Tom1234, password: @Tom1234
Basically, "VG9tMTIzNDpAVG9tMTIzNA==" is   "Tom1234:@Tom1234" 
```

Use this link to try to decode base64, then you will know: https://www.base64decode.org/


Go to sign.py, and you will know I use `generate_password_hash(password)` to save password.
So this workflow is a simple way to implement "saving password with hash" + "Auth Authorization: Basic"



PATCH:
Tom1234
#Tom123456

"""

def basic_auth_login_handler_get():
    if 'message' in auth.current_user() and type(auth.current_user()) == dict:
        if auth.current_user()['message'] == 'user is not found': return jsonify({'message': 'user is not found'}), 404
        if auth.current_user()['message'] == 'authentication failed': return jsonify({'message': 'authentication failed'}), 401
    if 'message' not in auth.current_user() and type(auth.current_user()) != dict:
        return "Hello, {}, you login successfully!".format(auth.current_user())


def basic_auth_reset_handler_patch():
    if 'message' in auth.current_user() and type(auth.current_user()) == dict:
        if auth.current_user()['message'] == 'user is not found': return jsonify({'message': 'user is not found'}), 404
        if auth.current_user()['message'] == 'authentication failed': return jsonify({'message': 'authentication failed'}), 401
    
    if not request.json:
        return 'no body', 400
    elif not 'password' in request.json: 
        return 'need password in body', 400

    password = request.json.get('password')
    match = check_password_valid_with_regex(password)
    if not match:
        return 'new password pattern is not right', 400
    no_full_width = is_no_full_width_char(password)
    if not no_full_width:
        return "new password pattern please don't include full-width", 400

    success, message = update_password_to_db(auth.current_user(), password)
    if success:
        return message, 200
    else:
        return message, 400
    


def check_password_valid_with_regex(password):
    """check password valid with regex based on rules below:
    1. at least one lower case
    2. at least one upper case
    3. at least one number
    4. at least one special symbol
    5. should between 8 - 20

    Args:
        password (str): the password that user want to signup
    """

    # This regex would give invalid if password contains full-width english alphabet, full-width special symbol, chinese kanji, ひらがな, カタカナ, japanese kanji
    # Would give valid if password contains full-width number string, ex: full-width -> "１" half-width -> "1"
    # But we want full-width number string to be invalid, so we will use "unicodedata.east_asian_width()" again to validate this.
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
    # compiling regex
    pattern = re.compile(reg)

    # searching regex                 
    match = re.search(pattern, password)
    return match


def is_no_full_width_char(str):
    """check if there is no full-width char in user_id and password
    Args:
        str (str): the password or user_id that user want to signup
    Return:
        True (bool): if no full_width char
        False (bool): if have full_width char, chinese kanji, ひらがな, カタカナ, japanese kanji
    """

    for char in str:
        status = unicodedata.east_asian_width(char)
        if status != "Na": return False
    else:
        return True

def update_password_to_db(user_id, password):
    """insert to db, and if success return success message or fail message
    
    Return:
        message (str): success message, or fail message
    """
    success = False

    exists = db.session.query(User).filter_by(user_id=user_id).first()
    if not exists:
        message = 'user id is not exist'
        return success, message

    hash_password = generate_password_hash(password)
    
    try:
        exists.password = hash_password
        db.session.commit()
        message = {
            "message": "password successfully reset",
            "user": {
                "user_id": user_id,
            }
        }
        success = True
    except Exception as ex:
        db.session.rollback()
        message = {
            "message": f"password reset is failed, {ex}",
            "user": {
                "user_id": user_id,
            }
        }
    finally:
        db.session.close()
    
    return success, message


def delete_user_in_db(user_id):
    """insert to db, and if success return success message or fail message
    
    Return:
        message (str): success message, or fail message
    """
    success = False

    exists = db.session.query(User).filter_by(user_id=user_id).first()
    if not exists:
        message = 'user id is not exist'
        return success, message
    
    try:
        User.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        message = {
            "message": "user successfully delete",
            "user": {
                "user_id": user_id,
            }
        }
        success = True
    except Exception as ex:
        db.session.rollback()
        message = {
            "message": f"user successfully delete is failed, {ex}",
            "user": {
                "user_id": user_id,
            }
        }
    finally:
        db.session.close()
    
    return success, message