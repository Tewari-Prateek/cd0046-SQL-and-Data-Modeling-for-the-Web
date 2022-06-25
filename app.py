#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import os
import config
from flask_migrate import Migrate
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
db.init_app(app)
moment = Moment(app)

# TODO: connect to a local postgresql database - done.

app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseURI.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(str(value))
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data. - done.
    # num_upcoming_shows should be aggregated
    # based on number of upcoming shows per venue.

    data = []
    areas = Venue.query.distinct(Venue.city, Venue.state).all()
    for area in areas:
        venues = Venue.query.filter_by(
            city=area.city).filter_by(state=area.state).all()
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": venues
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop"
    # and "Park Square Live Music & Coffee"
    searchTerm = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%' + searchTerm + '%')).all()
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template(
        'pages/search_venues.html', results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    # iterating over the shows and checking for the start time
    for show in shows:
        if show.start_time < datetime.now():
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        else:
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(","),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

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
    # on successful db insert, flash success
    form = VenueForm()
    if form.validate_on_submit():
        print("form validated")
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=','.join(form.genres.data),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,flash('An error occurred. Venue'+ data.name +'could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record.
    # Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              venue_id + ' could not be deleted.')
    else:
        flash('Venue ' + venue_id + ' was successfully deleted.')
    return render_template('pages/home.html')
    # BONUS CHALLENGE: Implement a button to delete a
    # Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then
    # redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database - done.
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search.
    # Ensure it is case-insensitive. - done.
    # seach for "A" should return "Guns N Petals", "Matt Quevado",
    # and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    data = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()
    response = {
        "count": len(data),
        "data": data
    }
    return render_template(
        'pages/search_artists.html',
        results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table,using artist_id

    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    # iterating over the shows and checking for the start time
    for show in shows:
        if show.start_time < datetime.now():
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        else:
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "address": artist.address,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    # db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
    # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))

# TODO: populate form with values from venue with ID <venue_id>
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    # db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
    


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
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
    form = ArtistForm()
    if form.validate_on_submit():
        print(form.name.data)
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=True if 'seeking_venue' in request.form else False,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,flash('An error occurred.Artist'+data.name+'could not be listed.')
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    shows = Show.query.all()
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db,
    # upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # on successful db insert, flash success
    if not error:
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    if error:
        flash('An error occurred. Show could not be listed.')
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
        Formatter(
            '%(asctime)s %(levelname)s:%(message)s[in %(pathname)s:%(lineno)d]'
        )
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
