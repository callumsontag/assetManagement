import re
from datetime import datetime

from flask import Flask, render_template

app = Flask(__name__)

messages = [{'title': 'message one',
             'content': 'message one content'},
            {'title': 'message two',
             'content': 'message two content'}
            ]


@app.route("/")
def login():
    return render_template('login.html', messages=messages)


@app.route("/create_asset")
def createAsset():
    return render_template("create_asset.html", messages=messages)


@app.route("/edit_asset")
def editAsset():
    return render_template("edit_asset.html", messages=messages)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", messages=messages)


@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    # Filter the name argument to letters only using regular expressions. URL arguments
    # can contain arbitrary text, so we restrict to safe characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content
