from pathlib import Path
import os
import random
from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman, GOOGLE_CSP_POLICY
from forms import RegisterForm, LoginForm, AssetForm
import logging
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'assetManagementDatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

talisman = Talisman(app, content_security_policy=GOOGLE_CSP_POLICY)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

# Configures logging
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('.app.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)


@login_manager.user_loader
def load_user(user_id):
    # user_id is the primary key of the user table, so is used in this query to load the user
    return User.query.get((user_id))


class User(UserMixin, db.Model):
    def get_id(self):
        return (self.user_id)
    user_id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Integer, default=0)
    attempted_logins = db.Column(db.Integer, default=0)
    # assets doesn't direct show on the User table itself but it represents the relationship
    # between the User and Assets Models, and allows the access
    # of the related Asset records associated with a particular user
    assets = db.relationship('Asset', backref='user', lazy=True)


class Asset(UserMixin, db.Model):
    asset_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    user_id = db.Column(db.String(50), db.ForeignKey(
        "user.user_id"), nullable=False)


@app.route('/')
def homepage():
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    try:
        if form.validate_on_submit():
            email = form.email.data
            first_name = form.firstName.data
            last_name = form.lastName.data
            password = form.password.data
            is_admin = False
            # user_id is randomly assigned a uuid
            user_id = str(uuid.uuid4())

            # if this returns a user, then the email already exists in database
            user = User.query.filter_by(email=email).first()

            if user:  # if a user is found, this redirects user back to register page so user can try again
                flash('An error occured during registration')
                logger.error(
                    'Registration attempted with email address already in use: %s', str(email))
                return redirect(url_for('register'))

            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'error')

            new_user = User(email=email, first_name=first_name, last_name=last_name, is_admin=is_admin, user_id=user_id,
                            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))

            # adds the new user to the database with a sha256 hashed password
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    except Exception as e:
        logger.error('An error occurred at register: %s', str(e))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()

            # take the user-supplied password, hash it, and compare it to the hashed password in the database
            if not user or not check_password_hash(user.password, password) or user.attempted_logins >= 5:
                flash('Please check your login details and try again.')
                user.attempted_logins += 1
                db.session.commit()
                logger.error('Invalid login attempt: %s', str(email))
                # if the user doesn't exist or password is wrong, renders the page with the previously entered email stored in the form
                return render_template('login.html', email=email)

            # if the above check passes, then we know the user has the right credentials and the user is taken to their assets page
            login_user(user)

            return redirect(url_for('assets', user_id=current_user.user_id))
    except Exception as e:
        logger.error('An error occurred at login: %s', str(e))
    return render_template('login.html', email="", form=form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    db.create_all()
    return render_template("home.html")


@app.route("/create_asset", methods=['GET', 'POST'])
@login_required
def create_asset():
    form = AssetForm()
    if form.validate_on_submit():
        # asset_id is randomly assigned a 10 digit id
        asset_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        name = form.asset.data
        description = form.assetDescription.data
        user_id = current_user.get_id()
        # adding a new asset to the asset database
        new_asset = Asset(asset_id=asset_id, name=name,
                          description=description, user_id=user_id)

        db.session.add(new_asset)
        db.session.commit()
        flash('Asset created successfully!')
    return render_template("create_asset.html", form=form)


@app.route("/edit_asset/<user_id>/<asset_id>", methods=["GET", "POST"])
@login_required
def edit_asset(user_id, asset_id):
    # takes the existing user id and asset id
    user = User.query.get(user_id)
    asset = Asset.query.get(asset_id)
    form = AssetForm(obj=asset)

    if user == current_user and asset:
        if form.validate_on_submit():
            asset.name = form.asset.data
            asset.description = form.assetDescription.data
            # replaces the existing assets name and description
            db.session.commit()
            return redirect(url_for('assets', user_id=user_id))
    else:
        return "Invalid permissions"
    return render_template("edit_asset.html", user=user, asset=asset, form=form)


@app.route("/assets/<user_id>")
@login_required
def assets(user_id):
    user = User.query.get(user_id)
    # ensures users can only view their own assets
    if user and user == current_user:
        # if user is admin then return all user assets
        if current_user.is_admin:
            assets = Asset.query.all()
            return render_template('assets.html', user=user, assets=assets)
        # otherwise just return the current users assets
        else:
            assets = user.assets
            return render_template('assets.html', user=user, assets=assets)
    else:
        return "Invalid permissions"


@app.route("/delete_asset/<user_id>/<asset_id>", methods=["GET", "POST"])
@login_required
def delete_asset(user_id, asset_id):
    user = User.query.get(user_id)
    asset = Asset.query.get(asset_id)

    # checks that the user is an admin, as only admins can delete assets
    if user == current_user and asset and current_user.is_admin:
        db.session.delete(asset)
        db.session.commit()
        return redirect(url_for('assets', user_id=user_id))
    else:
        logger.error(
            'Attempted delete assets request without permissions: %s', str(current_user))
        return "Access denied"


@app.route("/admin_view/<user_id>/", methods=["GET", "POST"])
@login_required
def admin_view(user_id):
    user = User.query.get(user_id)
    # checks that the user is an admin, as only admins can view all users
    if user == current_user and current_user.is_admin:
        users = User.query.all()
        return render_template('admin_view.html', user=user, users=users)
    else:
        logger.error(
            'Attempted admin view access without permissions: %s', str(current_user))
        return "Access denied"


@app.route("/reset_login/<user_id>", methods=["GET", "POST"])
@login_required
def reset_login(user_id):
    # checks that the user is an admin, as only admins can delete assets
    if current_user.is_admin:
        user = User.query.get(user_id)
        user.attempted_logins = 0
        db.session.commit()
        return redirect(url_for('admin_view', user_id=current_user.user_id))
    else:
        logger.error(
            'Attempted reset login attemps without permissions: %s', str(current_user))
        return "Access denied"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
