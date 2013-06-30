from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class FirstForm(Form):
    language = TextField('language', validators = [Required()])
    main_data = TextField('main_data', validators = [Required()])
    age = TextField('age', validators = [Required()])
