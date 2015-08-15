"""Utility file to seed data received from NYT API calls into database."""

from model import Article, Location, User, connect_to_db, db

from server import app

import json
import requests
import os

import sys

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']

# how to put API URI into a dictionary:
# http://docs.python-requests.org/en/latest/user/quickstart/#passing-parameters-in-urls

base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json"


url_params = {
        'q': '',    # search query term
        'fq': "glocations.contains:('LOCATION')",   # filtered search query
        'sort': 'newest',     # sort newest or oldest (API default is sort by relevance)
        'fl': '',       # list of fields - default is ALL
        'page': 'PAGE',     # default is page 0 (first page)
        'api-key': MY_NYT_KEY}


# FUNCTIONS NEEDED:
# have function signature in mind - name, params, return
# make a request to the api and json-ify it
# parse the response
# load articles into db
# load locations into db
# get lat/long
# later - load users into db


def load_locations(file_name):
    """ Load locations from text file into database.
        Run manually, passing in a file_name. """

        # first file to load: 'seed_data/locations.txt'

    locations_file = open(file_name)
    locations_by_line = locations_file.read().split('\n')
    for line in locations_by_line:
        location_info = line.split("|")
        location_name, latitude, longitude = location_info[0], location_info[1], location_info[2]
        new_location = Location(location_name=location_name, latitude=latitude, longitude=longitude)
        db.session.add(new_location)
    db.session.commit()


def api_call(location, page_number):
    """This function makes requests to the NYT API and receives JSON responses."""

    # update url based on location
    # is there another way to do this?
    url_params['fq'] = "glocations.contains:('%s')" % (location)
    url_params['page'] = page_number

    resp = requests.get(base_url, url_params)
    resp_json = resp.json()
    articles_list = resp_json['response']['docs']    # type(articles) = list





def load_articles(articles_list):
    """Load articles from API response into database.
    An article may be in the database more than once if it has multiple glocations."""

    for article in articles_list:
        keywords_list = article['keywords']
        for keyword in keywords_list:
            if keyword['name'] != 'glocations':
                continue
            else:
                glocation = keyword['value']
                web_url = article['web_url']
                headline = article['headline']['main']
                pub_date = article['pub_date']

                new_article = Article(glocation=glocation, web_url=web_url, headline=headline, pub_date=pub_date)

                db.session.add(new_article)

    db.session.commit()


def loop_api_call():
    for location 
    api_call()
    do api_call until 5 articles in database for that location

    while Article.query.


if __name__ == "__main__":
    connect_to_db(app)



    # load_locations('seed_data/locations.txt')


# def load_users():
