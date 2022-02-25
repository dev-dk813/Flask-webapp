from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from sqlalchemy.sql import func
from datetime import datetime
from os import path
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DDvrma3184'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

db = SQLAlchemy(app)

class Note(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    data= db.Column(db.String(10000))
    # date= db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model , UserMixin):
    id= db.Column(db.Integer, primary_key= True)
    email= db.Column(db.String(150), index=True, unique=True)
    password= db.Column(db.String(150))
    first_name= db.Column(db.String(150), index=True, unique=True)
    notes= db.relationship('Note')

@app.route("/", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note= Note(data=note, user_id = current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user= current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category="success")
                login_user(user, remember=True)
                return redirect('/')
            else:
                flash('Incorrect password', category="error")
        else:
            flash('Email does not exists', category="success")
    return render_template("login.html", user= current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # if len(email) < 4:
        #     flash('Email must be greater than 4 characters.', category="error")
        # elif len(first_name) < 2:
        #     flash('Name must be greater than 1 characters.', category="error")
        user = User.query.filter_by(email=email, first_name=first_name).first()
        if user:
            flash('Email already exists', category="error")
        elif password1 != password2:
            flash('Passwords doesn\'t match.', category="error")
        elif len(password1) < 6:
            flash('Password must be atleast 7 characters.', category="error")
        else:
            new_user = User(email=email, password= generate_password_hash(password1, method='sha256'), first_name=first_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category="success")
            return redirect('/')
    return render_template("sign_up.html", user= current_user)

@app.route("/delete-note", methods=['POST'])
def delete_data():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

# def create_database(app):
#     if not path.exists('DB_NAME'):
#     db.create_all(app=app)
#         print("Created Database!")


if __name__=="__main__":
    app.run(debug=True)