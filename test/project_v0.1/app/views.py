from flask import render_template, flash, redirect, session, url_for, request, g
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
    if form.validate_on_submit():
        getData = form.main_data.data
        text_index = form.text_index.data

        #saveData = open("data.txt", "a")
        #Remember Time first
        #saveData.write( time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time())) )
        #saveData.write("\n")
        #saveData.write(name)
        #saveData.write("\n")
        #saveData.write(getData)
        #saveData.write("\n")
        #saveData.write("\n")  
        #saveData.close()      
        

        user = User(text_index = text_index, main_data = getData)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('ThankYou'))

     # Start position
    #start = random.randint(1, 1+gap)
    start = 1
    # Gap
    gap = 3
   

    # Text
    select_text_index = random.choice(text_dict.keys())
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
        select_text_index = select_text_index
        )

@app.route('/ThankYou')
def ThankYou():
    return render_template('ThankYou.html')
