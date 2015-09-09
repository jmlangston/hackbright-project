"""Server for Jessica's Hackbright project."""

from flask import Flask, render_template, request, session, flash, redirect, jsonify

from model import Article, Location, User, Marker, Fav_Loc, connect_to_db, db

import json
import requests
import os

import geojson

import pprint

# create an instance of the Flask class
app = Flask(__name__)

# get API key from secrets.sh
MY_NYT_KEY = os.environ['MY_NYT_KEY']

app.secret_key = "ABC"


@app.route('/')
def welcome():
    """Renders HTML for welcome page."""

    # print session

    return render_template("welcome.html")


@app.route('/register', methods=["POST"])
def register_user():
    """Handles submission of user registration form. Adds user to session. Redirect to main map page with flash message."""

    username = request.form.get('username')
    password = request.form.get('password')

    # add new user to database
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    print new_user

    # get id of new user from database and put into session
    user = User.query.filter_by(username=username).first()

    if 'user_id' not in session:
        session['user_id'] = user.user_id

    # print session

    flash("Thank you for registering!")

    return redirect("/newsmap")


@app.route('/login', methods=["POST"])
def site_login():
    """Handles submission of user login form. Adds user to session. Redirect to main map page with flash message."""

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user:
        if password == user.password:
            session['user_id'] = user.user_id
            flash("Thank you for logging in!")
            return redirect("/newsmap")
        else:
            flash("The password you entered is incorrect. Please try again.")
            return redirect("/")
    else:
        flash("Please register.")
        return redirect("/")


@app.route('/logout')
def site_logout():
    """Removes user from session when they logout. Redirects to welcome page."""

    del session['user_id']

    flash("You are now logged out.")
    return redirect("/")


@app.route('/newsmap')
def show_map():
    """Renders main map view. Queries database for user's favorite locations and makes geoJSON feature collection to put markers on map."""

    # print session

    user_id = session.get('user_id')

    user = User.query.filter_by(user_id=user_id).first()

    fav_loc = db.session.query(Location).join(Fav_Loc).filter(Fav_Loc.user_id == user_id).all()

    marker_list = []

    locations = Location.query.all()
    for location in fav_loc:
        marker = Marker(location.location_name, location.longitude, location.latitude, location.location_id)
        marker_geojson = marker.generate_geojson()
        marker_list.append(marker_geojson)

    marker_collection = geojson.FeatureCollection(marker_list)

    return render_template("homepage.html", locations=locations, marker_collection=marker_collection, user=user, fav_loc=fav_loc)


@app.route('/new-location', methods=['POST'])
def add_new_location():
    """Add user's new favorite location to map."""
    
    user_id = session.get('user_id')
    location_id = int(request.form.get('location_id'))

    new_fav_loc = Fav_Loc(user_id=user_id, location_id=location_id)
    db.session.add(new_fav_loc)
    db.session.commit()

    location = Location.query.filter(Location.location_id == location_id).first()

    new_marker = Marker(location.location_name, location.longitude, location.latitude, location.location_id)

    marker_list = []
    marker_geojson = new_marker.generate_geojson()
    marker_list.append(marker_geojson)
    marker_collection = geojson.FeatureCollection(marker_list)

    return jsonify(location_name=location.location_name, marker_collection=marker_collection)


@app.route('/articles/<int:location_id>')
def show_list_articles(location_id):
    """Show list of articles about given location."""

    # query for articles by location
    articles = Article.query.filter_by(location_id=location_id).order_by(Article.pub_date.desc()).all()

    location = Location.query.filter_by(location_id=location_id).one()

    return render_template("articles_list.html", articles=articles, location=location)


# run the local server with this flask application
if __name__ == '__main__':
    connect_to_db(app)
    app.run(debug=True)
