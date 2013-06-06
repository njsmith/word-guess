from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class FirstForm(Form):
    name = TextField('name', validators = [Required()])
    word1 = TextField('word1', validators = [Required()])
