from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text_index = db.Column(db.String(1024), index = True, unique = False)
    main_data = db.Column(db.String(10240), index = True, unique = False)
