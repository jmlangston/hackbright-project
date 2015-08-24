"""Model for Jessica's Hackbright project. Defines database tables."""

# Manually create the database in the Python console:
# python -i model.py
# Connected to database for JML project.
# >>> db.create_all()


from flask_sqlalchemy import SQLAlchemy

# create an instance of the SQLAlchemy class to connect to the database
db = SQLAlchemy()


class Article(db.Model):
    """A news article from a NYT API call."""

    __tablename__ = "Articles"

    article_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    web_url = db.Column(db.String(128), nullable=False)
    headline = db.Column(db.String(128), nullable=False)
    glocation = db.Column(db.String(30), nullable=False)
    pub_date = db.Column(db.String(20), nullable=False)

    # see corresponding backref in Location class below
    location_id = db.Column(db.Integer, db.ForeignKey('Locations.location_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Article article_id=%d headline=%s glocation=%s location_id=%d>" % (self.article_id, self.headline, self.glocation, self.location_id)


class Location(db.Model):
    """A location that is the subject of news articles."""

    __tablename__ = "Locations"

    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_name = db.Column(db.String(30), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    article = db.relationship('Article', backref=db.backref('Locations'))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Location location_id=%d location_name=%s>" % (self.location_id, self.location_name)


# A helper/association/reference table to track users' favorite articles.
# https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships

favorite_articles = db.Table('Favorite_Articles',
    db.Column('fav_art_id', db.Integer, autoincrement=True, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('Users.user_id'), nullable=False),
    db.Column('article_id', db.Integer, db.ForeignKey('Articles.article_id'), nullable=False)
)

# A helper/association/reference table to track users' favorite locations.

favorite_locations = db.Table('Favorite_Locations',
    db.Column('fav_loc_id', db.Integer, autoincrement=True, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('Users.user_id'), nullable=False),
    db.Column('location_id', db.Integer, db.ForeignKey('Locations.location_id'), nullable=False)
)


class User(db.Model):
    """A user of the news-map application."""

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    # define relationships with Article and Location through the helper tables
    favorite_articles = db.relationship('Article', secondary=favorite_articles, backref=db.backref('Users'))
    favorite_locations = db.relationship('Location', secondary=favorite_locations, backref=db.backref('Users'))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%d username=%s>" % (self.user_id, self.username)


class Marker():
    """Generate GeoJSON feature object from a location object.
    In server.py, a GeoJSON FeaturesCollection will be passed to
    homepage.html in order to place markers on the map."""

    def __init__(self, location_name, longitude, latitude, location_id):
        self.location_name = location_name
        self.longitude = longitude
        self.latitude = latitude
        self.location_id = location_id

        self.articles = Article.query.filter_by(location_id=self.location_id).order_by('pub_date').first()

    def generate_geojson(self):

        return {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [self.longitude, self.latitude]
                    },
                    "properties": {
                        "title": self.location_name,
                        "description": self.location_id,
                        "articleUrl": '/articles/' + str(self.location_id),
                        "articles": self.articles.headline,
                    }
                }

        # return {
        #             "type": "Feature",
        #             "geometry": {
        #                 "type": "Point",
        #                 "coordinates": [self.longitude, self.latitude]
        #                 },
        #             "properties": {
        #                 "title": self.location_name,
        #                 "description": "News headlines will go here!"
        #             }
        #         }


########################

def connect_to_db(app):
    """Connect database and Flask application."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    print "Connected to database for JML project."
