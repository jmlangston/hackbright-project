"""Utility file to seed data into database."""

from model import Article, Location, User, Marker, connect_to_db, db

from server import app

import json
import requests
import os

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']


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

    # is there another way to update url based on location?

    url_params['fq'] = "glocations.contains:(%s)" % (location)
    url_params['page'] = page_number

    resp = requests.get(base_url, url_params)
    resp_json = resp.json()
    articles_list = resp_json['response']['docs']    # type(articles_list) = list
    return articles_list


def load_articles(articles_list, location):
    """Load articles_list obtained from send_api_request() into database."""

    # to do: is there a better way to get location_id for location?
    location_obj = Location.query.filter(Location.location_name == location).one()
    location_id = location_obj.location_id

    for article in articles_list:
        web_url = article['web_url']
        headline = article['headline']['main']
        pub_date = article['pub_date']

        new_article = Article(glocation=location, web_url=web_url, headline=headline, pub_date=pub_date, location_id=location_id)

        db.session.add(new_article)

    db.session.commit()


def loop_api_requests(location_name, num_articles):
    """Given a location, make API requests until the desired number of articles have been added to the database."""

    print "location_name: %s" % location_name

    # get location_id for location_name
    loc = Location.query.filter(Location.location_name == location_name).one()
    location_id = loc.location_id
    print "location_id: %d" % location_id

    initial_articles = Article.query.filter(Article.location_id == location_id).count()
    print "initial_articles: %d" % initial_articles

    # a single API request returns one 'page' with 10 articles
    pages_to_request = (int(num_articles) / 10) - 1

    page_number = 0

    while page_number <= pages_to_request:
        articles_list = send_api_request(location_name, page_number)
        load_articles(articles_list, location_name)
        page_number += 1

    current_articles = Article.query.filter(Article.location_id == location_id).count()

    print "current_articles: %d" % current_articles


###########################

if __name__ == "__main__":
    connect_to_db(app)
    print "Connected to database for JML project."
