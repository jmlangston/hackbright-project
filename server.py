"""Server for Jessica's Hackbright project."""

# import the Flask class
from flask import Flask, render_template

import json
import requests
import pprint
import os

pp = pprint.PrettyPrinter()

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']


# create an instance of the Flask class
app = Flask(__name__)

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/articles')
def show_list_articles():
    """Show list of articles about given location."""

    my_location = 'London'

    test_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?fq=glocations:(%s)&sort=newest&fl=web_url,snippet,source,multimedia,headline,keywords,pub_date&api-key=%s" % (my_location, MY_NYT_KEY)

    resp = requests.get(test_url)
    resp_json = resp.json()

    return render_template("articles_list.html", resp_json=resp_json)


# run the local server with this flask application
if __name__ == '__main__':
    app.run(debug=True)
