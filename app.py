#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<id: {self.id}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  tempdata = {'city':'','state':'','venues':[]}
  subdata = {}
  for city in db.session.query(Venue.city).distinct().order_by(Venue.city.desc()):
      tempdata['city'] = city[0]
      tempdata['state'] = db.session.query(Venue.state).filter(Venue.city==city[0]).distinct()[0][0]
      tempdata['venues'] = []
      for venue in db.session.query(Venue.id, Venue.name).filter(Venue.city==city[0]):
          subdata['id'] = venue[0]
          subdata['name'] = venue[1]
          subdata['num_upcoming_shows'] = db.session.query(Show.start_time).filter(Show.venue_id==venue[0], Show.start_time > datetime.now()).count()
          tempdata['venues'].append(subdata.copy())
      data.append(tempdata.copy())
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = {'count':0,'data':[]}
  tempdata = {'id':'','name':''}
  for venue in db.session.query(Venue.id, Venue.name).filter(Venue.name.match(request.form['search_term'])).order_by(Venue.id):
      tempdata['id'] = venue[0]
      tempdata['name'] = venue[1]
      tempdata['num_upcoming_shows'] = db.session.query(Show.start_time).filter(Show.venue_id==venue[0], Show.start_time > datetime.now()).count()
      data['count'] += 1
      data['data'].append(tempdata.copy())

  response=data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  tempdata = {'id':'','name':'','genres':[],'address':'','city':'','state':'','phone':'', 'website':'','facebook_link':'','seeking_talent':'','seeking_description':'','image_link':'','past_shows':[],'upcoming_shows':[],'past_shows_count':'','upcoming_shows_count':''}
  subdata = {}
  for venue in db.session.query(Venue.id, Venue.name, Venue.genres, Venue.address, Venue.city, Venue.state, Venue.phone, Venue.website, Venue.facebook_link, Venue.seeking_talent, Venue.seeking_description, Venue.image_link).order_by(Venue.id):
      pastShowsCount = 0
      upcomShowsCount = 0
      tempdata['id'] = venue[0]
      tempdata['name'] = venue[1]
      tempdata['genres'] = venue[2]
      tempdata['address'] = venue[3]
      tempdata['city'] = venue[4]
      tempdata['state'] = venue[5]
      tempdata['phone'] = venue[6]
      tempdata['website'] = venue[7]
      tempdata['facebook_link'] = venue[8]
      tempdata['seeking_talent'] = venue[9]
      tempdata['seeking_description'] = venue[10]
      tempdata['image_link'] = venue[11]
      tempdata['past_shows'] = []
      tempdata['upcoming_shows'] = []
      for show_venue in db.session.query(Venue.id, Show.id, Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Venue).join(Artist).filter(Venue.id==venue[0], Show.start_time < datetime.now()).order_by(Show.id):
          subdata['artist_id'] = show_venue[2]
          subdata['artist_name'] = show_venue[3]
          subdata['artist_image_link'] = show_venue[4]
          subdata['start_time'] = show_venue[5].isoformat()
          tempdata['past_shows'].append(subdata.copy())
          pastShowsCount += 1
      for show_venue in db.session.query(Venue.id, Show.id, Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Venue).join(Artist).filter(Venue.id==venue[0], Show.start_time > datetime.now()).order_by(Show.id):
          subdata['artist_id'] = show_venue[2]
          subdata['artist_name'] = show_venue[3]
          subdata['artist_image_link'] = show_venue[4]
          subdata['start_time'] = show_venue[5].isoformat()
          tempdata['upcoming_shows'].append(subdata.copy())
          upcomShowsCount += 1
      tempdata['past_shows_count'] = pastShowsCount
      tempdata['upcoming_shows_count'] = upcomShowsCount
      data.append(tempdata.copy())
  data1=data[0]
  data2=data[1]
  data3=data[2]
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      id = max(max(db.session.query(Venue.id).all())[0], max(db.session.query(Artist.id).all())[0]) + 1
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      genres = request.form.getlist('genres')
      website_link = request.form.get('website_link')
      if request.form.get('seeking_talent'):
          seeking_talent = True
      else:
          seeking_talent = False
      seeking_description = request.form.get('seeking_description')
      venue = Venue(id=id, name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres, website=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
      # on successful db insert, flash success
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
      flash('An error occurred. Venue could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      db.session.query(Venue).filter(Venue.id==venue_id).delete()
      db.session.commit()
  except:
      flash('An error occurred')
      db.session.rollback()
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  tempdata = {'id':'','name':''}
  for artist in db.session.query(Artist.id, Artist.name).distinct().order_by(Artist.id):
      tempdata['id'] = artist[0]
      tempdata['name'] = artist[1]
      data.append(tempdata.copy())
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = {'count':0,'data':[]}
  tempdata = {'id':'','name':''}
  for artist in db.session.query(Artist.id, Artist.name).filter(Artist.name.match(request.form['search_term'])).order_by(Artist.id):
      tempdata['id'] = artist[0]
      tempdata['name'] = artist[1]
      tempdata['num_upcoming_shows'] = db.session.query(Show.start_time).filter(Show.artist_id==artist[0], Show.start_time > datetime.now()).count()
      data['count'] += 1
      data['data'].append(tempdata.copy())

  response=data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = []
  tempdata = {'id':'','name':'','genres':[],'city':'','state':'','phone':'', 'website':'','facebook_link':'','seeking_venue':'','seeking_description':'','image_link':'','past_shows':[],'upcoming_shows':[],'past_shows_count':'','upcoming_shows_count':''}
  subdata = {}
  for artist in db.session.query(Artist.id, Artist.name, Artist.genres, Artist.city, Artist.state, Artist.phone, Artist.website, Artist.facebook_link, Artist.seeking_venue, Artist.seeking_description, Artist.image_link).order_by(Artist.id):
      pastShowsCount = 0
      upcomShowsCount = 0
      tempdata['id'] = artist[0]
      tempdata['name'] = artist[1]
      tempdata['genres'] = artist[2]
      tempdata['city'] = artist[3]
      tempdata['state'] = artist[4]
      tempdata['phone'] = artist[5]
      tempdata['website'] = artist[6]
      tempdata['facebook_link'] = artist[7]
      tempdata['seeking_venue'] = artist[8]
      tempdata['seeking_description'] = artist[9]
      tempdata['image_link'] = artist[10]
      tempdata['past_shows'] = []
      tempdata['upcoming_shows'] = []
      for show_artist in db.session.query(Artist.id, Show.id, Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Venue).join(Artist).filter(Artist.id==artist[0], Show.start_time < datetime.now()).order_by(Show.id):
          subdata['venue_id'] = show_artist[2]
          subdata['venue_name'] = show_artist[3]
          subdata['venue_image_link'] = show_artist[4]
          subdata['start_time'] = show_artist[5].isoformat()
          tempdata['past_shows'].append(subdata.copy())
          pastShowsCount += 1
      for show_artist in db.session.query(Artist.id, Show.id, Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Venue).join(Artist).filter(Artist.id==artist[0], Show.start_time > datetime.now()).order_by(Show.id):
          subdata['venue_id'] = show_artist[2]
          subdata['venue_name'] = show_artist[3]
          subdata['venue_image_link'] = show_artist[4]
          subdata['start_time'] = show_artist[5].isoformat()
          tempdata['upcoming_shows'].append(subdata.copy())
          upcomShowsCount += 1
      tempdata['past_shows_count'] = pastShowsCount
      tempdata['upcoming_shows_count'] = upcomShowsCount
      data.append(tempdata.copy())
  data1=data[0]
  data2=data[1]
  data3=data[2]
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  form_artist = db.session.query(Artist).get(artist_id)
  artist={
    "id": form_artist.id,
    "name": form_artist.name,
    "genres": form_artist.genres,
    "city": form_artist.city,
    "state": form_artist.state,
    "phone": form_artist.phone,
    "website": form_artist.website,
    "facebook_link": form_artist.facebook_link,
    "seeking_venue": form_artist.seeking_venue,
    "seeking_description": form_artist.seeking_description,
    "image_link": form_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
      artist = db.session.query(Artist).get(artist_id)
      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      artist.image_link = request.form.get('image_link')
      artist.facebook_link = request.form.get('facebook_link')
      artist.genres = request.form.getlist('genres')
      artist.website_link = request.form.get('website_link')
      if request.form.get('seeking_talent'):
          artist.seeking_talent = True
      else:
          artist.seeking_talent = False
      artist.seeking_description = request.form.get('seeking_description')
      db.session.commit()
  except:
      flash('An error occurred')
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  form_venue = db.session.query(Venue).get(venue_id)
  venue={
    "id": form_venue.id,
    "name": form_venue.name,
    "genres": form_venue.genres,
    "address": form_venue.address,
    "city": form_venue.city,
    "state": form_venue.state,
    "phone": form_venue.phone,
    "website": form_venue.website,
    "facebook_link": form_venue.facebook_link,
    "seeking_talent": form_venue.seeking_talent,
    "seeking_description": form_venue.seeking_description,
    "image_link": form_venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
      venue = db.session.query(Venue).get(venue_id)
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      venue.image_link = request.form.get('image_link')
      venue.facebook_link = request.form.get('facebook_link')
      venue.genres = request.form.getlist('genres')
      venue.website_link = request.form.get('website_link')
      if request.form.get('seeking_talent'):
          venue.seeking_talent = True
      else:
          venue.seeking_talent = False
      venue.seeking_description = request.form.get('seeking_description')
      db.session.commit()
  except:
      flash('An error occurred')
      db.session.rollback()
  finally:
      db.session.close()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    id = max(max(db.session.query(Venue.id).all())[0], max(db.session.query(Artist.id).all())[0]) + 1
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    if request.form.get('seeking_venue'):
        seeking_venue = True
    else:
        seeking_venue = False
    seeking_description = request.form.get('seeking_description')
    artist = Artist(id=id, name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres, website=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    # on successful db insert, flash success
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Artist could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  tempdata = {'venue_id':'','venue_name':'','artist_id':'','artist_name':'','artist_image_link':'','start_time':''}
  for show in db.session.query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time, Show.id).join(Venue).join(Artist).order_by(Show.id):
      tempdata['venue_id'] = show[0]
      tempdata['venue_name'] = show[1]
      tempdata['artist_id'] = show[2]
      tempdata['artist_name'] = show[3]
      tempdata['artist_image_link'] = show[4]
      tempdata['start_time'] = show[5].isoformat()
      data.append(tempdata.copy())
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      id = max(db.session.query(Show.id).all())[0] + 1
      venue_id = request.form.get('venue_id')
      artist_id = request.form.get('artist_id')
      start_time = request.form.get('start_time')
      show = Show(id=id, venue_id=venue_id, artist_id=artist_id, start_time=start_time)
      # on successful db insert, flash success
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
