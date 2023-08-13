from flask import session, render_template, url_for, redirect, request, render_template_string, make_response, send_file
from src import app, db
from flask_session import Session
import json


@app.route('/')
@app.route('/index')
def index():
    return render_template('homepage.html') 

@app.route('/login', methods=['GET'])
def login():
    if 'logged' in session and session['logged']:
        return redirect(url_for('logout'))
    return render_template('auth.html', err=request.args.get('err')) 

@app.route('/login', methods=['POST'])
def login_post():
    if 'logged' in session and session['logged']:
        return redirect(url_for('login'))
    username = request.form.get('login')
    password = request.form.get('password')
    user = db.get_user_by_name(username)
    if user == None:
        return redirect(url_for('login', err=1))
    session['user_id'] = user[0][0]
    session['logged'] = True
    if user[0][3] != password:
        return redirect(url_for('login', err=1))
    return redirect(url_for('index'))

@app.route('/register', methods=['GET'])
def register():
    if 'logged' in session and session['logged']:
        return redirect(url_for('index'))
    return render_template('reg.html', err=request.args.get('err'))

@app.route('/register', methods=['POST'])
def register_post():
    if 'logged' in session and session['logged']:
        return redirect(url_for('index'))
    username = request.form.get('username')
    personal_data = request.form.get('personalData')
    password = request.form.get('password')
    password_rep = request.form.get('passwordRep')
    if password != password_rep:
        return redirect(url_for('register', err=2))
    if db.get_user_by_name(username) != None:
        return redirect(url_for('register', err=1))
    user_id = db.insert_user(username, password, personal_data)
    session['user_id'] = user_id
    session['logged'] = True
    return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
def logout():
    session['logged'] = False
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET'])
def profile():
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    user = db.get_user_by_id(session['user_id'])[0]
    apps = db.get_appointments_by_userid(session['user_id'])
    if apps == None:
        apps = []
    return render_template('userProfile.html', user=user, apps=apps)

@app.route('/appointments/create', methods=['GET'])
def create_app():
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    return render_template('visitForm.html', doctors=json.dumps({'list': db.get_all_doctors()}))

@app.route('/appointments/create', methods=['POST'])
def create_app_post():
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    fio = request.form.get('fio')
    time = request.form.get('timeStamp')
    ins_num = request.form.get('insNum')
    doctor = request.form.get('doctor')
    app_id = db.create_appointment(session['user_id'], doctor, fio, ins_num, time)
    return redirect(url_for('info_app', appid=app_id))

@app.route('/appointments/<appid>/info', methods=['GET'])
def info_app(appid):
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    app_info = db.get_appointment_by_id(appid)[0]
    doctor = db.get_doctor_by_name(app_info[2])[0]
    return render_template('appointCurrent.html', appinfo=app_info, doctor=doctor)

@app.route('/api-dev/users', methods=['GET'])
def get_users():
    return {'list': db.get_all_users()}

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_file(app.root_path + '/static' + request.path)

@app.errorhandler(404)
def page_not_found(e):
    error_page = open('src/templates/404.html').read().replace('_PATH_', request.path)
    return render_template_string(error_page), 404
