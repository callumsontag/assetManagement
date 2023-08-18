from pathlib import Path
import re
import os
import sqlite3
import random
from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'assetManagementDatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    def get_id(self):
        return (self.user_id)
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(1000))
    last_name = db.Column(db.String(1000))
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Integer, default=0)
    assets = db.relationship('Asset', backref='user', lazy=True)


class Asset(UserMixin, db.Model):
    asset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)


@app.route('/')
def homepage():
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        password = request.form['password']
        is_admin = False
        user_id = ''.join(str(random.randint(0, 9)) for _ in range(10))

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address ia already in use')
            return redirect(url_for('register'))

        new_user = User(email=email, first_name=first_name, last_name=last_name, is_admin=is_admin, user_id=user_id,
                        password=generate_password_hash(password, method='sha256'))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # login code goes here
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('login', user_id=current_user.user_id))

        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        return redirect(url_for('assets'))
    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route("/create_asset", methods=['GET', 'POST'])
@login_required
def create_asset():
    if request.method == 'POST':
        asset_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        name = request.form['name']
        description = request.form['description']
        user_id = current_user.get_id()

        new_asset = Asset(asset_id=asset_id, name=name,
                          description=description, user_id=user_id)

        db.session.add(new_asset)
        db.session.commit()
        flash('Asset created')
        print(new_asset)
    return render_template("create_asset.html")


@app.route("/edit_asset/<int:user_id>/<int:asset_id>", methods=["GET", "POST"])
def edit_asset(user_id, asset_id):
    user = User.query.get(user_id)
    asset = Asset.query.get(asset_id)

    if user and asset:
        if request.method == "POST":
            asset.name = request.form["new_asset_name"]
            asset.description = request.form["new_asset_description"]
            db.session.commit()
            return
        redirect(url_for('assets', user_id=user_id))
    else:
        return "User or asset not found"
    return render_template("edit_asset.html", user=user, asset=asset)


@app.route("/assets/<int:user_id>")
@login_required
def assets(user_id):

    user = User.query.get(user_id)
    if user:
        assets = user.assets
        return render_template('assets.html', user=user, assets=assets)
    else:
        return "User not found"


@app.route('/delete_asset/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id):
    # if current_user.is_admin:
    #     conn = sqlite3.connect('assetManagementDatabase.db')
    #     cursor = conn.cursor()
    #     # Your code to delete the asset from the database
    #     cursor.execute('DELETE FROM assets WHERE asset_id = ?', (asset_id,))
    #     conn.commit()
    #     conn.close()
    #     return redirect(url_for('assets'))
    # else:
    #     return "Access denied"  # Only admins can delete assets
    return render_template('assets.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
