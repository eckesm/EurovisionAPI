# from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

import string
import random

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


def generate_random_string(length, unique_callback):
    unique_string = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=length))
    while(unique_callback(unique_string) != None):
        unique_string = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=length))
    return unique_string


def convert_date(original_date):
    if original_date != None:
        converted_date = original_date.strftime('%d-%m-%Y')
        return converted_date
    return original_date


def convert_time(original_time):
    if original_time != None:
        updated_time = original_time.strftime(
            "%H:%M")
        return updated_time
    else:
        return original_time


class Participant(db.Model):
    """Participant model."""

    __tablename__ = 'participants'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)

    entries = db.relationship(
        'Entry', backref='participant', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'description': self.description,
            'entries': [entry.id for entry in self.entries],
            'countries_represented': [entry.country.id for entry in self.entries],
            'performances': [performance.id for performance in self.get_performances()],
            'events': [performance.event_id for performance in self.get_performances()]
        }

    def get_performances(self):
        return db.session.query(Event_Entry).filter(Participant.id == self.id).join(Entry).order_by(Entry.year).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def get_all(cls):
        # return cls.query.all()
        return db.session.query(Participant).order_by(Participant.name).all()

    @classmethod
    def get_choices(cls):
        return [participant.id for participant in Participant.query.all()]

    @classmethod
    def register(cls, name, image_url, description):
        """Add new participant to database."""

        new_participant = cls(id=generate_random_string(
            10, cls.get_by_id), name=name, image_url=image_url, description=description)
        db.session.add(new_participant)
        db.session.commit()
        return new_participant

    @classmethod
    def update(cls, participant, name, image_url, description):
        """Update participant."""

        participant.name = name
        participant.image_url = image_url
        participant.description = description
        db.session.add(participant)
        db.session.commit()
        return participant

    @classmethod
    def delete(cls, id):
        """Delete participant from database."""

        participant = cls.get_by_id(id)
        db.session.delete(participant)
        db.session.commit()
        return "deleted"


class Country(db.Model):
    """Country model."""

    __tablename__ = 'countries'

    id = db.Column(db.String(3), primary_key=True)
    country = db.Column(db.Text, nullable=False)
    flag_image_url = db.Column(db.Text, nullable=True)

    entries = db.relationship(
        'Entry', backref='country', cascade='all, delete-orphan')

    events = db.relationship(
        'Event', backref='country', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'country': self.country,
            'flag_image_url': self.flag_image_url,
            'entries': [entry.id for entry in self.entries],
            'events': [event.id for event in self.events],
            'participants': [entry.participant_id for entry in self.entries],
            'performances': [performance.id for performance in self.get_performances()]
        }

    def get_performances(self):
        return db.session.query(Event_Entry).filter(Country.id == self.id).join(Event).order_by(Event.year).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    @ classmethod
    def get_all(cls):
        # return cls.query.all()
        return db.session.query(Country).order_by(Country.country).all()

    @ classmethod
    def get_choices(cls):
        return [country.id for country in Country.query.all()]

    @ classmethod
    def register(cls, id, country, flag_image_url):
        """Add new country to database."""

        new_country = cls(id=id.upper(), country=country,
                          flag_image_url=flag_image_url)
        db.session.add(new_country)
        db.session.commit()
        return new_country

    @ classmethod
    def update(cls, country, country_name, flag_image_url):
        """Update country."""

        country.country = country_name
        country.flag_image_url = flag_image_url
        db.session.add(country)
        db.session.commit()
        return country

    @ classmethod
    def delete(cls, id):
        """Delete country from database."""

        country = cls.get_by_id(id)
        db.session.delete(country)
        db.session.commit()
        return "deleted"


class Entry(db.Model):
    """Entry model."""

    __tablename__ = 'entries'

    id = db.Column(db.Text, primary_key=True)
    participant_id = db.Column(db.Text, db.ForeignKey('participants.id'))
    country_id = db.Column(db.Text, db.ForeignKey('countries.id'))
    title = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    eurovision_resource_url = db.Column(db.Text, nullable=True)
    eurovision_video_url = db.Column(db.Text, nullable=True)
    music_video_url = db.Column(db.Text, nullable=True)
    spotify_url = db.Column(db.Text, nullable=True)
    written_by = db.Column(db.Text, nullable=True)
    composed_by = db.Column(db.Text, nullable=True)
    broadcaster = db.Column(db.Text, nullable=True)
    lyrics = db.Column(db.Text, nullable=True)
    lyrics_language = db.Column(db.Text, nullable=True)
    lyrics_english = db.Column(db.Text, nullable=True)

    performances = db.relationship(
        'Event_Entry', backref='entry', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'participant': self.participant.name,
            'country_id': self.country_id,
            'country': self.country.country,
            'title': self.title,
            'year': self.year,
            'eurovision_resource_url': self.eurovision_resource_url,
            'eurovision_video_url': self.eurovision_video_url,
            'music_video_url': self.music_video_url,
            'spotify_url': self.spotify_url,
            'written_by': self.written_by,
            'composed_by': self.composed_by,
            'broadcaster': self.broadcaster,
            'lyrics': self.lyrics,
            'lyrics_language': self.lyrics_language,
            'lyrics_english': self.lyrics_english,
            'performances': [performance.id for performance in self.performances],
            'events': [event.id for event in self.get_events()]
        }

    def get_events(self):
        return db.session.query(Event).filter(Entry.id == self.id).join(Event_Entry).order_by(Event.date).all()

    @ classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    @ classmethod
    def get_by_props(cls, country_id, year):
        return cls.query.filter_by(country_id=country_id, year=year).one_or_none()

    @ classmethod
    def get_all(cls):
        # return cls.query.all()
        return db.session.query(Entry).order_by(Entry.title).all()

    @ classmethod
    def get_choices(cls):
        return [entry.id for entry in Entry.query.all()]

    @ classmethod
    def register(cls, participant_id, country_id, title, year, eurovision_resource_url, eurovision_video_url, music_video_url, spotify_url, written_by, composed_by, broadcaster, lyrics, lyrics_language, lyrics_english):
        """Add new entry to database."""

        new_entry = cls(id=generate_random_string(
            10, cls.get_by_id), participant_id=participant_id, country_id=country_id, title=title, year=year, eurovision_resource_url=eurovision_resource_url, eurovision_video_url=eurovision_video_url, music_video_url=music_video_url, spotify_url=spotify_url, written_by=written_by, composed_by=composed_by, broadcaster=broadcaster, lyrics=lyrics, lyrics_language=lyrics_language, lyrics_english=lyrics_english)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @ classmethod
    def update(cls, entry, participant_id, country_id, title, year, eurovision_resource_url, eurovision_video_url, music_video_url, spotify_url, written_by, composed_by, broadcaster, lyrics, lyrics_language, lyrics_english):
        """Update entry."""

        entry.participant_id = participant_id
        entry.country_id = country_id
        entry.title = title
        entry.year = year
        entry.eurovision_resource_url = eurovision_resource_url
        entry.eurovision_video_url = eurovision_video_url
        entry.music_video_url = music_video_url
        entry.spotify_url = spotify_url
        entry.written_by = written_by
        entry.composed_by = composed_by
        entry.broadcaster = broadcaster
        entry.lyrics = lyrics
        entry.lyrics_language = lyrics_language
        entry.lyrics_english = lyrics_english
        db.session.add(entry)
        db.session.commit()
        return entry

    @ classmethod
    def delete(cls, id):
        """Delete entry from database."""

        entry = cls.get_by_id(id)
        db.session.delete(entry)
        db.session.commit()
        return "deleted"


class Event(db.Model):
    """Event model."""

    __tablename__ = 'events'

    id = db.Column(db.Text, primary_key=True)
    event = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    eurovision_resource_url = db.Column(db.Text, nullable=True)
    recap_video_url = db.Column(db.Text, nullable=True)
    video_playlist_url = db.Column(db.Text, nullable=True)
    spotify_playlist_url = db.Column(db.Text, nullable=True)
    host_city = db.Column(db.Text, nullable=False)
    host_country_id = db.Column(db.Text, db.ForeignKey('countries.id'))

    performances = db.relationship(
        'Event_Entry', backref='event', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'event': self.event,
            'type': self.type,
            'year': self.year,
            'date': convert_date(self.date),
            'start_time': convert_time(self.start_time),
            'end_time': convert_time(self.end_time),
            'eurovision_resource_url': self.eurovision_resource_url,
            'recap_video_url': self.recap_video_url,
            'video_playlist_url': self.video_playlist_url,
            'spotify_playlist_url': self.spotify_playlist_url,
            'host_city': self.host_city,
            'host_country_id': self.country.id,
            'host_country': self.country.country,
            'performances': [performance.id for performance in self.performances],
            'entries': [entry.id for entry in self.get_entries()],
            'participating_countries': [entry.country_id for entry in self.get_entries()]
        }

    def get_entries(self):
        return db.session.query(Entry).filter(Event.id == self.id).join(Event_Entry).order_by(Entry.country_id).all()

    @ classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    @ classmethod
    def get_by_props(cls, event, type, year):
        return cls.query.filter_by(event=event, type=type, year=year).one_or_none()

    @ classmethod
    def get_all(cls):
        # return cls.query.all()
        return db.session.query(Event).order_by(Event.date.desc(), Event.event).all()

    @ classmethod
    def get_choices(cls):
        return [event.id for event in Event.query.all()]

    @ classmethod
    def register(cls, event, type, year, date, start_time, end_time, eurovision_resource_url, recap_video_url, video_playlist_url, spotify_playlist_url, host_city, host_country_id):
        """Add new entry to database."""

        new_event = cls(id=generate_random_string(
            10, cls.get_by_id), event=event, type=type, year=year, date=date, start_time=start_time, end_time=end_time, eurovision_resource_url=eurovision_resource_url, recap_video_url=recap_video_url, video_playlist_url=video_playlist_url, spotify_playlist_url=spotify_playlist_url, host_city=host_city, host_country_id=host_country_id)
        db.session.add(new_event)
        db.session.commit()
        return new_event

    @ classmethod
    def update(cls, event, event_name, type, year, date, start_time, end_time, eurovision_resource_url, recap_video_url, video_playlist_url, spotify_playlist_url, host_city, host_country_id):
        """Update event."""

        event.event = event_name
        event.type = type
        event.year = year
        event.date = date
        event.start_time = start_time
        event.end_time = end_time
        event.eurovision_resource_url = eurovision_resource_url
        event.recap_video_url = recap_video_url
        event.video_playlist_url = video_playlist_url
        event.spotify_playlist_url = spotify_playlist_url
        event.host_city = host_city
        event.host_country_id = host_country_id
        db.session.add(event)
        db.session.commit()
        return event

    @ classmethod
    def delete(cls, id):
        """Delete event from database."""

        event = cls.get_by_id(id)
        db.session.delete(event)
        db.session.commit()
        return "deleted"


class Event_Entry(db.Model):
    """Performance model."""

    __tablename__ = 'events_entries'

    id = db.Column(db.Text, primary_key=True)
    event_id = db.Column(db.Text, db.ForeignKey('events.id'))
    entry_id = db.Column(db.Text, db.ForeignKey('entries.id'))
    points = db.Column(db.Integer, nullable=True)
    place = db.Column(db.Integer, nullable=True)
    qualified = db.Column(db.Text, nullable=True)
    running_order = db.Column(db.Integer, nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'entry': self.entry.title,
            'event_id': self.event_id,
            'event': self.event.event,
            'points': self.points,
            'place': self.place,
            'qualified': self.qualified,
            'running_order': self.running_order,
            'participant_id': self.entry.participant.id,
            'participant': self.entry.participant.name,
            'country_id': self.entry.country.id,
            'country': self.entry.country.country
        }

    @ classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    @ classmethod
    def get_by_ids(cls, event_id, entry_id):
        return cls.query.filter_by(event_id=event_id, entry_id=entry_id).one_or_none()

    @ classmethod
    def get_all(cls):
        return cls.query.all()

    @ classmethod
    def get_choices(cls):
        return [performance.id for performance in Event_Entry.query.all()]

    @ classmethod
    def register(cls, event_id, entry_id, points, place, qualified, running_order):
        """Add new event-entry to database."""

        new_performance = cls(id=generate_random_string(
            10, cls.get_by_id), event_id=event_id, entry_id=entry_id,
            points=points, place=place, qualified=qualified, running_order=running_order)
        db.session.add(new_performance)
        db.session.commit()
        return new_performance

    @ classmethod
    def update(cls, performance, event_id, entry_id, points, place, qualified, running_order):
        """Update performance."""

        performance.event_id = event_id
        performance.entry_id = entry_id
        performance.points = points
        performance.place = place
        performance.qualified = qualified
        performance.running_order = running_order
        db.session.add(performance)
        db.session.commit()
        return performance

    @ classmethod
    def delete(cls, id):
        """Delete performance from database."""

        performance = cls.get_by_id(id)
        db.session.delete(performance)
        db.session.commit()
        return "deleted"
