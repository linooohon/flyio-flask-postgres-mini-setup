import re
import unicodedata


from werkzeug.security import generate_password_hash

from flask import Blueprint
signup = Blueprint('signup', __name__)

from flask import request, make_response, jsonify

from backend import db
from backend.models import User


@signup.route('/signup', methods=['GET', 'POST'])
def signup_handler():
    if request.method == 'GET':
        return 'signup get'
    fail_body = False

    # basic check
    if not request.json: 
        fail_body = make_signup_fail_response_body()
    elif not 'user_id' in request.json: 
        fail_body = make_signup_fail_response_body('user_id')
    elif not 'password' in request.json: 
        fail_body = make_signup_fail_response_body('password')
    
    if fail_body: 
        return make_response(jsonify(fail_body), 400)

    # get user_id, password in request payload
    user_id, password = get_userId_and_password(request)

    # check password and user_id validation with regex
    match = check_user_id_valid_with_regex(user_id)
    if not match: 
        fail_body = make_signup_fail_response_body('user_id', match)
    
    match = check_password_valid_with_regex(password)
    if not match:
        fail_body = make_signup_fail_response_body('password', match)

    # check password and user_id validation with unicodedata.east_asian_width()
    match = True
    no_full_width = is_no_full_width_char(user_id)
    if not no_full_width:
        fail_body = make_signup_fail_response_body('user_id', match, no_full_width)

    no_full_width = is_no_full_width_char(password)
    if not no_full_width:
        fail_body = make_signup_fail_response_body('password', match, no_full_width)

    if fail_body: 
        return make_response(jsonify(fail_body), 400)


    success, message = insert_to_db(user_id, password)
    if success:
        success_body = message
        return make_response(jsonify(success_body), 200)
    else:
        fail_body = message
        return make_response(jsonify(fail_body), 400)


def check_user_id_valid_with_regex(user_id):
    """check user_id valid with regex based on rules below:
    1. at least one lower case
    2. at least one upper case
    3. at least one number
    4. should between 6 - 20

    Args:
        user_id (str): the user_id that user want to signup
    """

    # This regex would give invalid if password contains full-width english alphabet, full-width special symbol, chinese kanji, ひらがな, カタカナ, japanese kanji
    # Would give valid if password contains full-width number string, ex: full-width -> "１" half-width -> "1"
    # But we want full-width number string to be invalid, so we will use "unicodedata.east_asian_width()" again to validate this.
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{6,20}$"
    # compiling regex
    pattern = re.compile(reg)

    # searching regex                 
    match = re.search(pattern, user_id)
    return match


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

def make_signup_fail_response_body(str=None, match=True, no_full_width=True):
    """make http fail response body during signup
    Args:
        str (str): 'password' or 'user_id'
    """
    fail_body = {
        "message": "Account creation failed",
        "cause": "required user_id and password"
    }
    if str and match and no_full_width:
        fail_body = {
            "message": "Account creation failed",
            "cause": f"required {str}"
        }
    if str and not match:
        fail_body = {
            "message": "Account creation failed",
            "cause": f"{str} pattern is not right, please follow the rules."
        }

    if str and not no_full_width:
        fail_body = {
            "message": "Account creation failed",
            "cause": f"{str} pattern is not right, please use half-width only."
        }
    return fail_body


def get_userId_and_password(request):
    """get user_id and password in request payload"""
    user_id = request.json.get('user_id')
    password = request.json.get('password')
    return user_id, password


def insert_to_db(user_id, password):
    """insert to db, and if success return success message or fail message
    
    Return:
        message (str): success message, or fail message
    """
    success = False

    exists = db.session.query(User._id).filter_by(user_id=user_id).first()
    if exists:
        message = 'user id is already exist'
        return success, message

    hash_password = generate_password_hash(password)
    
    user = User(user_id, hash_password)
    try:
        db.session.add(user)
        db.session.commit()
        message = {
            "message": "Account successfully created",
            "user": {
                "user_id": user_id,
                "nickname": password
            }
        }
        success = True
    except Exception as ex:
        db.session.rollback()
        message = {
            "message": f"The data insert is failed, {ex}",
            "user": {
                "user_id": user_id,
                "nickname": password
            }
        }
    finally:
        db.session.close()
    
    return success, message