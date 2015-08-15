"""Server for Jessica's Hackbright project."""

# import the Flask class
from flask import Flask, render_template

from model import Article, Location, User, connect_to_db, db

import json
import requests
import os

import pprint

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']


# create an instance of the Flask class
app = Flask(__name__)


@app.route('/')
def index():
    """Homepage."""

    # query database for locations and display them

    locations = Location.query.all()

    return render_template("homepage.html", locations=locations)


@app.route('/articles/<int:location_id>')
def show_list_articles(location_id):
    """Show list of articles about given location."""

    # query for articles by location

    articles = Article.query.filter_by(location_id=location_id).order_by('pub_date').all()

    location = Location.query.filter_by(location_id=location_id).all()

    return render_template("articles_list.html", articles=articles, location=location)


# run the local server with this flask application
if __name__ == '__main__':
    connect_to_db(app)
    app.run(debug=True)
