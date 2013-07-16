from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    worker_id = db.Column(db.String(1024), index = True, unique = False)
    text_index = db.Column(db.String(1024), index = True, unique = False)
    start_position = db.Column(db.String(1024), index = True, unique = False)
    gap = db.Column(db.String(1024), index = True, unique = False)
    main_data = db.Column(db.String(10240), index = True, unique = False)
