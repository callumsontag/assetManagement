from pathlib import Path
import os
import random
from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'assetManagementDatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)


@login_manager.user_loader
def load_user(user_id):
    # user_id is the primary key of the user table, so is used in this query to load the user
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    def get_id(self):
        return (self.user_id)
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Integer, default=0)
    # assets doesn't direct show on the User table itself but it represents the relationship
    # between the User and Assets Models, and allows the access
    # of the related Asset records associated with a particular user
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
        # user_id is randomly assigned a 10 digit user id
        user_id = ''.join(str(random.randint(0, 9))
                          for _ in range(10))

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        if user:  # if a user is found, this redirects user back to register page so user can try again
            flash('Email address ia already in use')
            return redirect(url_for('register'))

        new_user = User(email=email, first_name=first_name, last_name=last_name, is_admin=is_admin, user_id=user_id,
                        password=generate_password_hash(password, method='sha256'))

        # adds the new user to the database with a sha256 hashed password
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, renders the page with the previously entered email stored in the form
            return render_template('login.html', email=email)

        # if the above check passes, then we know the user has the right credentials and the user is taken to their assets page
        login_user(user)
        return redirect(url_for('assets', user_id=current_user.user_id))
    return render_template('login.html', email="")


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route("/create_asset", methods=['GET', 'POST'])
@login_required
def create_asset():
    if request.method == 'POST':
        # randomly assigned 10 digit asset id
        asset_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        name = request.form['name']
        description = request.form['description']
        user_id = current_user.get_id()
        # adding a new asset to the asset database
        new_asset = Asset(asset_id=asset_id, name=name,
                          description=description, user_id=user_id)

        db.session.add(new_asset)
        db.session.commit()
        flash('Asset created!')
        print(new_asset)
    return render_template("create_asset.html")


@app.route("/edit_asset/<int:user_id>/<int:asset_id>", methods=["GET", "POST"])
def edit_asset(user_id, asset_id):
    # takes the existing user id and asset id
    user = User.query.get(user_id)
    asset = Asset.query.get(asset_id)

    if user and asset:
        if request.method == "POST":
            asset.name = request.form["new_asset_name"]
            asset.description = request.form["new_asset_description"]
            # replaces the existing assets name and description
            db.session.commit()
            return redirect(url_for('assets', user_id=user_id))
    else:
        return "User or asset not found"
    return render_template("edit_asset.html", user=user, asset=asset)


@app.route("/assets/<int:user_id>")
@login_required
def assets(user_id):
    user = User.query.get(user_id)

    if user:
        # if user is admin then return all user assets
        if current_user.is_admin:
            assets = Asset.query.all()
            return render_template('assets.html', user=user, assets=assets)
        # otherwise just return the current users assets
        else:
            assets = user.assets
            return render_template('assets.html', user=user, assets=assets)
    else:
        return "User not found"


@app.route("/delete_asset/<int:user_id>/<int:asset_id>", methods=["GET", "POST"])
@login_required
def delete_asset(user_id, asset_id):
    user = User.query.get(user_id)
    asset = Asset.query.get(asset_id)

    # checks that the user is an admin, as only admins can delete assets
    if user and asset and current_user.is_admin:
        db.session.delete(asset)
        db.session.commit()
        return redirect(url_for('assets', user_id=user_id))
    else:
        return "Access denied, only admins can delete assets"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
