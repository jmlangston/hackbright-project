"""Utility file to seed data into database."""

from model import Article, Location, User, Marker, connect_to_db, db

from server import app

import json
import requests
import os

import sys

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']

# how to put API URI into a dictionary:
# http://docs.python-requests.org/en/latest/user/quickstart/#passing-parameters-in-urls

# REMEMBER:
# have a function's 'signature' in mind - function name, params, what it returns

# Future functions in this file could include:
# def load_users():
# get lat/long for new location (with NYT Geo API, or other)


base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json"

url_params = {
        'fq': "glocations.contains:('LOCATION')",   # filtered search query
        'sort': 'newest',     # sort newest or oldest (API default is sort by relevance)
        'fl': 'web_url,headline,keywords,pub_date',
        'page': 'PAGE',     # default is page 0 (first page)
        'api-key': MY_NYT_KEY}


def load_locations(file_name):
    """ Load locations from text file into database.
        Run manually, passing in a file_name. """

    # first file loaded: 'seed_data/locations.txt'

    locations_file = open(file_name)
    locations_by_line = locations_file.read().split('\n')
    for line in locations_by_line:
        location_info = line.split("|")
        location_name, latitude, longitude = location_info[0], location_info[1], location_info[2]
        new_location = Location(location_name=location_name, latitude=latitude, longitude=longitude)
        db.session.add(new_location)
    db.session.commit()

    # TO DO LATER: have this function add UNIQUE locations
    # use verify_location_in_db()


def verify_location_in_db(location):
    """Given a location, returns True or False depending on if
    that location is in the Locations table."""

    loc_tuples = db.session.query(Location.location_name).all()
    loc_list = []
    for tup in loc_tuples:
        loc_list.append(tup[0])

    if location in loc_list:
        return True
    else:
        return False


def send_api_request(location, page_number):
    """This function makes requests to the NYT API and receives JSON responses."""

    # update url based on location
    # is there another way to do this?

    url_params['fq'] = "glocations.contains:(%s)" % (location)
    url_params['page'] = page_number

    resp = requests.get(base_url, url_params)
    resp_json = resp.json()
    articles_list = resp_json['response']['docs']    # type(articles_list) = list
    return articles_list


def load_articles(articles_list, location):
    """Load articles_list obtained from send_api_request() into database."""

    # Future possibilities:
    # An article may be in the db more than once if it has multiple glocations.
    # If I end up using this function without an indicated location,
    # have it be able to add new locations to the database

    # TO DO: better way to do this?
    # get location_id for location
    location_obj = Location.query.filter(Location.location_name == location).one()
    location_id = location_obj.location_id

    # for testing
    # print location_id
    # print "Article list length: %d" % (len(articles_list))

    for article in articles_list:
        web_url = article['web_url']
        headline = article['headline']['main']
        pub_date = article['pub_date']

        # for testing
        # print headline, pub_date
        # print ''

        new_article = Article(glocation=location, web_url=web_url, headline=headline, pub_date=pub_date, location_id=location_id)

        db.session.add(new_article)

    db.session.commit()


# TO DO: have loop_api_request() take in a desired number of articles

def loop_api_requests(loc_name):
    """Given a location, make API calls until there are the desired number_of_articles for
    that location in the database."""

    # find location, location_id in database
    loc = Location.query.filter(Location.location_name==loc_name).one()
    loc_id = loc.location_id

    page_number = 0

    # previously written as below but ended up infinitely looping
    # while articles_in_db <= number_of_articles:
    while page_number < 4:
        articles_list = send_api_request(loc_name, page_number)
        load_articles(articles_list, loc_name)
        page_number += 1

    # for testing
    # articles_in_db = Article.query.filter(Article.location_id==loc_id).count()
    # print "articles_in_db = %d" % articles_in_db


if __name__ == "__main__":
    connect_to_db(app)
    print "Connected to database for JML project."
