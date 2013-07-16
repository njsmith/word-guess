from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class FirstForm(Form):
    worker_id = TextField('worker_id', validators = [Required()])
    text_index = TextField('text_index', validators = [Required()])
    start_position = TextField('start_position', validators = [Required()])
    gap = TextField('gap', validators = [Required()])
    main_data = TextField('main_data', validators = [Required()])
