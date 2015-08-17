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
        'fq': "glocations.contains:('LOCATION')",   # filtered search query
        'sort': 'newest',     # sort newest or oldest (API default is sort by relevance)
        'fl': 'web_url,headline,keywords,pub_date',
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


# TO DO LATER: add UNIQUE locations


# TO DO LATER: change function names to verb_noun

def api_call(location, page_number):
    """This function makes requests to the NYT API and receives JSON responses."""

    # update url based on location
    # is there another way to do this?

    url_params['fq'] = "glocations.contains:(%s)" % (location)
    url_params['page'] = page_number

    resp = requests.get(base_url, url_params)
    resp_json = resp.json()
    articles_list = resp_json['response']['docs']    # type(articles_list) = list
    return articles_list


test_list = api_call("NEW YORK CITY", 0)


def locations_in_db(location):
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


def load_articles(articles_list, location):
    """Load articles_list from API response into database.
    An article may be in the database more than once if it has multiple glocations."""

    # TO DO LATER - add additional glocations to database

    # list_loc_db = str(db.session.query(Location.location_name).all())
    # print list_loc_db

    # get location_id for location
    # TO DO: better way to do this?
    location_obj = Location.query.filter(Location.location_name == location).one()
    location_id = location_obj.location_id
    print location_id


    print "Article list length: %d" % (len(articles_list))

    for article in articles_list:
        web_url = article['web_url']
        headline = article['headline']['main']
        pub_date = article['pub_date']

        # for testing
        print headline, pub_date

        # keywords_list = article['keywords']

        # for testing
        # print keywords_list
        print ''


        # TO DO: I can actually take out the part below
        # where I get the glocation from the API response.
        # In order to have the location in the format I want it
        # for the database, I need to pass it in to this function.


        # for keyword in keywords_list:
        #     if keyword['name'] == 'glocations':
        #         if keyword['name'] in list_loc_db:
        #             print "SUCCESS!"
        #             glocation = keyword['value']
                    # location_obj = Location.query.filter(Location.location_name == str(glocation).upper()).one()
        #             location_id = location_obj.location_id
        #             new_article = Article(glocation=glocation, web_url=web_url, headline=headline, pub_date=pub_date, location_id=location_id)
        #             db.session.add(new_article)
        #             print "new article added about %s !!!!!!" % (glocation)
        #     else:
        #         continue

        new_article = Article(glocation=location, web_url=web_url, headline=headline, pub_date=pub_date, location_id=location_id)

        db.session.add(new_article)


    db.session.commit()


def loop_api_call(loc_name, number_of_articles):
    """Given a location, make API calls until there are the desired number_of_articles for
    that location in the database."""

    loc = Location.query.filter(Location.location_name==loc_name).one()

    articles_in_db = Article.query.filter_by(loc.location_id).count()
    page_number = 0

    while articles_in_db <= number_of_articles:
        api_call(loc_name, page_number)
        load_articles(articles_list)
        page_number += 1


if __name__ == "__main__":
    connect_to_db(app)
    print "Connected to database for JML project."

    # load_locations('seed_data/locations.txt')


# def load_users():
