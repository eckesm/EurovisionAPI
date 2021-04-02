from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField, DateField, BooleanField, TimeField
from wtforms.validators import ValidationError, InputRequired, Optional, Length, URL, NumberRange


class ParticipantForm(FlaskForm):
    """Form for participants."""

    class Meta:
        csrf = False

    name = StringField("Name", validators=[InputRequired()])
    image_url = StringField("Eurovision Resource URL", validators=[
        Optional(), URL(message="Must be a valid URL.")])
    description = StringField("description", validators=[Optional()])


class CountryForm(FlaskForm):
    """Form for countries."""

    class Meta:
        csrf = False

    id = StringField("Country", validators=[InputRequired(), Length(
        min=3, max=3, message="Country ID must be exactly 3 letters.")])
    country = StringField("Country", validators=[
                          InputRequired(message="Country name is required.")])
    flag_image_url = StringField("Eurovision Resource URL", validators=[
                                 Optional(), URL(message="Must be a valid URL.")])

class CountryUpdateForm(FlaskForm):
    """Form for updating countries."""

    class Meta:
        csrf = False

    country = StringField("Country", validators=[
                          InputRequired(message="Country name is required.")])
    flag_image_url = StringField("Eurovision Resource URL", validators=[
                                 Optional(), URL(message="Must be a valid URL.")])


class EntryForm(FlaskForm):
    """Form for entries."""

    class Meta:
        csrf = False

    participant_id = SelectField("Participant ID", validators=[
                                 InputRequired()])
    country_id = SelectField("County ID", validators=[
                             InputRequired()])
    title = StringField("Title", validators=[
                        InputRequired(message="Song title required.")])
    year = IntegerField("Year", validators=[InputRequired(), NumberRange(
        min=1956, message="Must be at least 1956.")])
    eurovision_resource_url = StringField("Eurovision Resource URL", validators=[
        Optional(), URL(message="Must be a valid URL.")])
    eurovision_video_url = StringField("Eurovision Video URL", validators=[
        Optional(), URL(message="Must be a valid URL.")])
    music_video_url = StringField("Music Video URL", validators=[
                                  Optional(), URL(message="Must be a valid URL.")])
    spotify_url = StringField("Spotify URL", validators=[
                              Optional(), URL(message="Must be a valid URL.")])
    written_by = StringField("Written By", validators=[Optional()])
    composed_by = StringField("Composed By", validators=[Optional()])
    broadcaster = StringField("Broadcaster", validators=[Optional()])
    lyrics = TextAreaField("Original Lyrics", validators=[Optional()])
    lyrics_language = TextAreaField(
        "Original Language", validators=[Optional()])
    lyrics_english = TextAreaField("English Lyrics", validators=[Optional()])


class EventForm(FlaskForm):
    """Form for events."""

    class Meta:
        csrf = False

    event = StringField("Event name", validators=[InputRequired()])
    type = SelectField("Event type", validators=[InputRequired()])
    year = IntegerField("Year", validators=[InputRequired(), NumberRange(
        min=1956, message="Must be at least 1956.")])
    date = DateField("Date", validators=[Optional()])
    start_time = TimeField("Start time", validators=[Optional()])
    end_time = TimeField("End time", validators=[Optional()])
    eurovision_resource_url = StringField("Eurovision Resource URL", validators=[
                                          Optional(), URL(message="Must be a valid URL.")])
    recap_video_url = StringField("Recap video URL", validators=[
                                          Optional(), URL(message="Must be a valid URL.")])
    video_playlist_url = StringField("Video playlist URL", validators=[
                                          Optional(), URL(message="Must be a valid URL.")])
    spotify_playlist_url = StringField("Spotify playlist URL", validators=[
                                          Optional(), URL(message="Must be a valid URL.")])
    host_city = StringField("Host city", validators=[InputRequired()])
    host_country_id = SelectField(
        "Host country ID", validators=[InputRequired()])


class EventEntryForm(FlaskForm):
    """Form for performances."""

    class Meta:
        csrf = False

    event_id = SelectField("Event ID", validators=[InputRequired()])
    entry_id = SelectField("Entry ID", validators=[InputRequired()])
    points = IntegerField("Points", validators=[
                          Optional(), NumberRange(min=0, message=("Must be at least 0."))])
    place = IntegerField("Place", validators=[Optional(), NumberRange(
        min=0, message=("Must be at least 0."))])
    qualified = SelectField("Qualified?", validators=[Optional()])
    running_order = IntegerField("Running order", validators=[
                                 Optional(), NumberRange(min=0, message=("Must be at least 0."))])
