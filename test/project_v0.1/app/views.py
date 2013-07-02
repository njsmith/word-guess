from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, FirstForm
from models import User, ROLE_USER, ROLE_ADMIN

from texts import text_dict
import time
import random

# index view function suppressed for brevity

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html',
        title = 'Home',
        user = user,
        posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/FirstForm', methods = ['GET', 'POST'])
def FillFirstForm():
    form = FirstForm()
    if request.method == 'POST':
        print form.validate_on_submit()
        print form.errors
    if form.validate_on_submit():
        language = form.language.data
        getData = form.main_data.data
        age = form.age.data
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
        

        user = User(nickname = "Tester", email = "abc", role = ROLE_USER, language = language, age = age, text_index = text_index, main_data = getData)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('ThankYou'))

    # Start position
    start = 1
    # Gap
    gap = 100

    # Text
    select_text_index = random.randint(0,17)
    if select_text_index == 16:
        select_text_index = 18
    if select_text_index == 17:
        select_text_index = 19
    select_text = text_dict[select_text_index]
    iniNum = 0
    parag_num = len(select_text)
    paraglen = [iniNum for i in range(20)]
    for parag in range (0, parag_num):
        paraglen[parag] = len(select_text[parag])
        print paraglen[parag]

   

    return render_template('FirstForm.html', 
        title = 'First Form',
        form = form,
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
