from flask import render_template, flash, redirect, session, url_for, request, g, send_file
from app import app, db, lm, oid
from forms import FirstForm
from models import User, ROLE_USER, ROLE_ADMIN

from texts import text_dict, title_dict
import time
import random

# index view function suppressed for brevity

@app.route('/', methods = ['GET', 'POST'])
@app.route('/FirstForm', methods = ['GET', 'POST'])
def FillFirstForm():
    form = FirstForm()
    if request.method == 'POST':
        print form.validate_on_submit()
        print form.errors
    #if form.validate_on_submit():
        print 'Got it!'
        getWorker_id = request.form["worker_id"]
        getData = request.form["result"]
        getText_index = request.form["text_index"]
        getStart_position = request.form["start_position"]
        getGap = request.form["gap"]
        #getWorker_id = form.worker_id.data
        #getData = form.main_data.data
        #getText_index = form.text_index.data
        #getStart_position = form.start_position.data
        #getGap = form.gap.data

        user = User(worker_id = getWorker_id, text_index = getText_index, start_position = getStart_position, gap = getGap, main_data = getData)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('ThankYou'))

    if request.args["assignmentId"] == "ASSIGNMENT_ID_NOT_AVAILABLE":
        is_preview = True
    else:
        is_preview = False

    worker_id = None
    if "workerId" in request.args:
        worker_id = request.args["workerId"]
        
    available_text = text_dict.keys()
    have_done = User.query.filter_by(worker_id = worker_id)
    for hit in have_done:
        removed = int(hit.text_index)
        print 'Removed: ' + str(removed)
        available_text.remove(removed)
    print available_text
    if len(available_text) == 0 :
        return render_template('Repeat.html')

    # Gap
    gap = 300
    # Start position
    start = random.randint(1, 1+gap)
    #start = 1
   
    # Text
    select_text_index = random.choice(available_text)
    select_text = text_dict[select_text_index]
    select_title = title_dict[select_text_index]
    iniNum = 0
    parag_num = len(select_text)
    paraglen = [iniNum for i in range(20)]
    for parag in range (0, parag_num):
        paraglen[parag] = len(select_text[parag])
        print paraglen[parag]

    return render_template('FirstForm.html', 
        title = 'First Form',
        form = form,
        text_title = select_title,
        text = (select_text ),
        textlen = len(select_text) ,
        paraglen = paraglen,
        start = start,
        gap = gap,
        select_text_index = select_text_index,
        is_preview = is_preview,
        worker_id = worker_id
        )

@app.route('/ThankYou')
def ThankYou():
    return render_template('ThankYou.html')

@app.route('/Repeat')
def Repeat():
    return render_template('Repeat.html')

@app.route("/mmturkey.js")
def mmturkey():
    return send_file("static/mmturkey/mmturkey.js")
