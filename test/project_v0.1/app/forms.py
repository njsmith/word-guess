from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class FirstForm(Form):
    main_data = TextField('main_data', validators = [Required()])
    text_index = TextField('text_index', validators = [Required()])
