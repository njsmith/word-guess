from flask import render_template, flash, redirect, session, url_for, request, g, send_file
from app import app, db #, lm, oid
from forms import FirstForm
from models import User, Pending, Disappear,  ROLE_USER, ROLE_ADMIN

from texts import text_dict, title_dict
import time
import random
import uuid

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
        getHit_id = request.form["hit_id"]
        
        # Add finished data to DB
        user = User(id = getHit_id, worker_id = getWorker_id, text_index = getText_index, start_position = getStart_position, gap = getGap, main_data = getData)
        db.session.add(user)
        db.session.commit()

        # Delete same ID in Pending DB
        for hit in (Pending.query
                     .filter_by(id = getHit_id)):
            db.session.delete(hit)
        db.session.commit()

        return redirect(url_for('ThankYou'))
    
    # Check expired pending
    Pending.expire(db.session)
    if request.args["assignmentId"] == "ASSIGNMENT_ID_NOT_AVAILABLE":
        is_preview = True
    else:
        is_preview = False

    worker_id = None
    if "workerId" in request.args:
        worker_id = request.args["workerId"]
        
    # Any text have not done by this worker
    available_text = text_dict.keys()

    have_done = User.query.filter_by(worker_id = worker_id)
    for hit in have_done:
        removed = int(hit.text_index)
        if removed in available_text:
            available_text.remove(removed)
    if len(available_text) == 0 :
        return redirect(url_for('Repeat'))

    # Check the least text number
    counts = {}
    for text in available_text:
        count = (User.query.filter_by(text_index = text).count()
                 + Pending.query.filter_by(text_index = text).count())
        counts[text] = count
    min_count = min(counts.values())
    best_texts = []
    for text in available_text:
        if counts[text] == min_count:
            best_texts.append(text)

    # temp_least = 99999
    # need_remove = []
    # # Find out the least done number of texts
    # for count in available_text:
    #     current_count = User.query.filter_by(text_index = count).count() + Pending.query.filter_by(text_index = count).count()
    #     if current_count < temp_least:
    #         temp_least = current_count
    # # If the done number of the text is larger than the least done number
    # # Put this text into need_remove list
    # for count in available_text:
    #     current_count = User.query.filter_by(text_index = count).count() + Pending.query.filter_by(text_index = count).count()
    #     if current_count > temp_least:
    #         need_remove.append(count)
    # # Remove illegal text from available_text list
    # available_text = list(set(available_text)-set(need_remove)) 

    # Gap
    gap = 4
    # Generate a ID for this HIT
    hit_id = uuid.uuid4().hex
   
    # Text
    select_text_index = random.choice(best_texts)
    select_text = text_dict[select_text_index]
    select_title = title_dict[select_text_index]
    iniNum = 0
    parag_num = len(select_text)
    paraglen = [iniNum for i in range(20)]
    for parag in range (0, parag_num):
        paraglen[parag] = len(select_text[parag])
        print paraglen[parag]

    # the number test need to be done for each position
    number_each_position = 20
    select_text_number = User.query.filter_by(text_index = select_text_index).count()
    # Start position
    start = 5
    #start = (gap + 1) - (select_text_number / number_each_position)
    #if start < 1:
    #start = random.randint(1, 1+gap)

    #When sent user a text
    #save a copy to Pending as well
    if not is_preview:
        pending = Pending(id = hit_id, worker_id = worker_id, text_index = select_text_index, start_position = start, gap = gap, start_time = time.time())
        db.session.add(pending)
        db.session.commit()

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
        worker_id = worker_id,
        hit_id = hit_id
        )

@app.route('/Disappear', methods = ['POST'])
def disappear():
    #if form.validate_on_submit():
    getWorker_id = request.form["worker_id"]
    getData = request.form["result"]
    getText_index = request.form["text_index"]
    getStart_position = request.form["start_position"]
    getGap = request.form["gap"]
    getHit_id = request.form["hit_id"]

    # Add finished data to DB
    disappear = Disappear(id = getHit_id, worker_id = getWorker_id, text_index = getText_index, start_position = getStart_position, gap = getGap, main_data = getData)
    db.session.add(disappear)
    db.session.commit()

    # Delete same ID in Pending DB
    for hit in (Pending.query
                 .filter_by(id = getHit_id)):
        db.session.delete(hit)
    db.session.commit()
    return "bye"

@app.route('/ThankYou')
def ThankYou():
    return render_template('ThankYou.html')

@app.route('/Repeat')
def Repeat():
    return render_template('Repeat.html')

@app.route("/mmturkey.js")
def mmturkey():
    return send_file("static/mmturkey/mmturkey.js")
