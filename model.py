"""Model for Jessica's Hackbright project. Defines database tables."""

from flask_sqlalchemy import SQLAlchemy

# create an instance of the SQLAlchemy class to connect to the database
db = SQLAlchemy()

class Article(db.Model):
    """A news article from a NYT API call."""

    __tablename__ = "Articles"

    article_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    web_url = db.Column(db.String(128), nullable=False)
    snippet = db.Column(db.String, nullable=False)
    multimedia = db.Column(db.String, nullable=False)
    headline = db.Column(db.String, nullable=False)
    glocation = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.String, nullable=False)
    location_id = db.Column(db.String, db.ForeignKey('Locations.location_id'), nullable=False)

    # TO DO: designate location_id as foreign key

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Article article_id=%d headline=%s glocation=%s location_id=%d>" % (self.article_id, self.headline, self.glocation, self.location_id)


class Location(db.Model):
    """A location that is the subject of news articles."""

    __tablename__ = "Locations"

    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_name = db.Column(db.String, nullable=False)
    location_api_code = db.Column(db.String, nullable=False)
    # TO DO: lat
    # TO DO: long

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Location location_id=%d location_name=%s location_api_code=%s>" % (self.location_id, self.location_name, self.location_api_code)


class User(db.Model):
    """A user of the news-map application."""

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    # TO DO - REFERENCE TABLE... ids of favorite locations
    # TO DO - REFERENCE TABLE... ids of favorite articles
    # TO DO: designate foreign keys

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%d username=%s>" % (self.user_id, self.username)
