from backend import db

class User(db.Model):
    __tablename__ = 'users'
    
    _id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.String())
    password = db.Column('password', db.String())

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password

    def __repr__(self):
        return '<id {}>'.format(self._id)
