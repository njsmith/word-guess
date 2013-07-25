from app import db
import time

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.String, primary_key = True)
    worker_id = db.Column(db.String, index = True, unique = False)
    text_index = db.Column(db.Integer, index = True, unique = False)
    start_position = db.Column(db.Integer, index = True, unique = False)
    gap = db.Column(db.Integer, index = True, unique = False)
    main_data = db.Column(db.String)

class Pending(db.Model):
    id = db.Column(db.String, primary_key = True)
    worker_id = db.Column(db.String, index = True, unique = False)
    text_index = db.Column(db.Integer, index = True, unique = False)
    start_position = db.Column(db.Integer, index = True, unique = False)
    gap = db.Column(db.Integer, index = True, unique = False)
    start_time = db.Column(db.Float)

    @classmethod
    def expire(cls, session):
        now = time.time()
        duration_hours = 1
        last_good_start_time = now - ( duration_hours * 60 * 60 )
        for hit in (cls.query
                     .filter(cls.start_time < last_good_start_time)):
            session.delete(hit)
        session.commit()

class Disappear(db.Model):
    id = db.Column(db.String, primary_key = True)
    worker_id = db.Column(db.String, index = True, unique = False)
    text_index = db.Column(db.Integer, index = True, unique = False)
    start_position = db.Column(db.Integer, index = True, unique = False)
    gap = db.Column(db.Integer, index = True, unique = False)
    main_data = db.Column(db.String)
