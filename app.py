from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from functools import wraps
from models import db, connect_db, Participant, Country, Entry, Event, Event_Entry
from forms import ParticipantForm, CountryForm, EntryForm, EventForm, EventEntryForm, CountryUpdateForm
import os
import sys
import datetime
# import json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV')
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)


EVENT_TYPE_LIST = ['contest', 'semi-final', 'final']
API_KEY = os.environ.get('API_KEY')


def api_key_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('API-Key', None)
        response = check_API_credentials(api_key)
        if response != True:
            return response
        return func(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------------


def check_API_credentials(api_key):
    if api_key != API_KEY or api_key == None:
        response = {
            "status": "fail",
            "message": "Must provide valid API key."
        }
        return (jsonify(response), 401)

    else:
        return True

#####################################################################
# ------------------------ View Functions ------------------------- #
#####################################################################

@app.route('/')
def show_api_welcome_page():

    return render_template('api_information.html')


#####################################################################
# ------------------------- Participants -------------------------- #
#####################################################################


@app.route('/participants', methods=['POST'])
def add_participant():

    # check API credentials
    api_key = request.headers.get('API-Key', None)
    response = check_API_credentials(api_key)
    if response != True:
        return response

    # validate form
    form = ParticipantForm()
    if form.validate():

        # prevent creation of duplicate resource
        participant_name = request.json.get('name', None)
        existing_participant = Participant.get_by_name(participant_name)

        if existing_participant != None:
            response = {
                "status": "duplicate",
                "message": f"{existing_participant.name} already exists in the database with ID {existing_participant.id}.",
                "participant": existing_participant.serialize()
            }
            return jsonify(response)

        # create new resource
        data = {k: v for k, v in request.json.items()}
        new_participant = Participant.register(
            data.get('name', None),
            data.get('image_url', None),
            data.get('description', None))
        response = {
            "status": "success",
            "participant": new_participant.serialize(),
            "message": f"{data['name']} added to participants."
        }
        return (jsonify(response), 201)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@app.route('/participants', methods=['GET'])
def get_all_participants():

    response = {
        "participants": [participant.serialize() for participant in Participant.get_all()]
    }
    return jsonify(response)

# -------------------------------------------------------------------


@app.route('/participants/<participant_id>', methods=['GET'])
def get_participant(participant_id):

    participant = Participant.get_by_id(participant_id)

    if participant != None:
        response = {
            "participant": participant.serialize()
        }
        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no participant with id {participant_id}."
        }
        return (jsonify(response), 404)

# -------------------------------------------------------------------


@app.route('/participants/<participant_id>', methods=['PATCH', 'PUT'])
def update_participant(participant_id):

    # check API credentials
    response = check_API_credentials(request.json.get('api_key', None))
    if response != True:
        return response

    participant = Participant.get_by_id(participant_id)
    if participant == None:
        response = {
            "status": "not found",
            "message": f"There is no participant with id {participant_id}."
        }
        return (jsonify(response), 404)

    # validate form
    form = ParticipantForm()
    if form.validate():

        # prevent creation of duplicate resource
        participant_name = request.json.get('name', None)
        existing_participant = Participant.get_by_name(participant_name)

        if existing_participant != None and existing_participant.id != participant_id:
            response = {
                "status": "duplicate",
                "message": f"{existing_participant.name} already exists in the database with ID {existing_participant.id}.",
                "participant": existing_participant.serialize()
            }
            return jsonify(response)

        # update resource
        data = {k: v for k, v in request.json.items()}
        updated_participant = Participant.update(
            participant,
            data.get('name', None),
            data.get('image_url', None),
            data.get('description', None))

        response = {
            "status": "success",
            "participant": updated_participant.serialize(),
            "message": f"{updated_participant.name} updated."
        }
        return jsonify(response)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@app.route('/participants/<participant_id>', methods=['DELETE'])
def delete_participant(participant_id):

    # check API credentials
    response = check_API_credentials(request.json.get('api_key', None))
    if response != True:
        return response

    participant = Participant.get_by_id(participant_id)
    if participant != None:

        status = Participant.delete(participant_id)
        if status == "deleted":
            response = {
                "deleted": participant_id,
                "status": "success",
                "message": f"Participant with id {participant_id} has been deleted."
            }

        else:
            response = {
                "status": "error",
                "message": f"There was an error deleting participant with id {participant_id}."
            }

        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no participant with id {participant_id}."
        }
        return (jsonify(response), 404)


#####################################################################
# -------------------------- Countries ---------------------------- #
#####################################################################

@app.route('/countries', methods=['POST'])
@api_key_required
def add_country():

    # validate form
    form = CountryForm()
    if form.validate():

        # prevent creation of duplicate resource
        country_id = request.json.get('id', None)
        existing_country = Country.get_by_id(country_id)

        if existing_country != None:
            response = {
                "status": "duplicate",
                "message": f"{existing_country.id} already exists in the database as {existing_country.country}.",
                "country": existing_country.serialize()
            }
            return jsonify(response)

        # create new resource
        data = {k: v for k, v in request.json.items()}
        new_country = Country.register(
            data.get("id", None),
            data.get("country", None),
            data.get("flag_image_url", None))
        response = {
            "status": "success",
            "country": new_country.serialize(),
            "message": f"{data['country']} added to countries."
        }
        return (jsonify(response), 201)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)


# -------------------------------------------------------------------

@app.route('/countries', methods=['GET'])
def get_all_countries():

    response = {
        "countries": [country.serialize() for country in Country.get_all()]
    }
    return jsonify(response)

# -------------------------------------------------------------------


@app.route('/countries/<country_id>', methods=['GET'])
def get_country(country_id):

    country = Country.get_by_id(country_id)

    if country != None:
        response = {
            "country": country.serialize()
        }
        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no country with id {country_id}."
        }
        return (jsonify(response), 404)

# -------------------------------------------------------------------


@app.route('/countries/<country_id>', methods=['PATCH', 'PUT'])
@api_key_required
def update_country(country_id):

    country = Country.get_by_id(country_id)
    if country == None:
        response = {
            "status": "not found",
            "message": f"There is no country with id {country_id}."
        }
        return (jsonify(response), 404)

    form = CountryUpdateForm()
    if form.validate():

        # update resource
        data = {k: v for k, v in request.json.items()}
        updated_country = Country.update(
            country,
            data.get('country', None),
            data.get('flag_image_url', None))

        response = {
            "status": "success",
            "country": updated_country.serialize(),
            "message": f"{updated_country.country} updated."
        }
        return jsonify(response)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/countries/<country_id>', methods=['DELETE'])
@api_key_required
def delete_country(country_id):

    country = Country.get_by_id(country_id)
    if country != None:

        status = Country.delete(country_id)
        if status == "deleted":
            response = {
                "deleted": country_id,
                "status": "success",
                "message": f"Country with id {country_id} has been deleted."
            }

        else:
            response = {
                "status": "error",
                "message": f"There was an error deleting country with id {country_id}."
            }

        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no country with id {country_id}."
        }
        return (jsonify(response), 404)

#####################################################################
# ---------------------------- Entries ---------------------------- #
#####################################################################


@ app.route('/entries', methods=['POST'])
@api_key_required
def add_entry():

    # validate form
    form = EntryForm()
    form.participant_id.choices = Participant.get_choices()
    form.country_id.choices = Country.get_choices()
    if form.validate():

        # prevent creation of duplicate resource
        country_id = request.json.get('country_id', None)
        year = request.json.get('year', None)
        existing_entry = Entry.get_by_props(country_id, year)

        if existing_entry != None:
            response = {
                "status": "duplicate",
                "message": "An entry for this year and country already exists in the database.",
                "entry": existing_entry.serialize()
            }
            return jsonify(response)

        # create new resource
        data = {k: v for k, v in request.json.items()}
        new_entry = Entry.register(data.get("participant_id", None),
                                   data.get("country_id", None),
                                   data.get("title", None),
                                   data.get("year", None),
                                   data.get("eurovision_resource_url", None),
                                   data.get("eurovision_video_url", None),
                                   data.get("music_video_url", None),
                                   data.get("spotify_url", None),
                                   data.get("written_by", None),
                                   data.get("composed_by", None),
                                   data.get("broadcaster", None),
                                   data.get("lyrics", None),
                                   data.get("lyrics_language", None),
                                   data.get("lyrics_english", None))
        response = {
            "status": "success",
            "entry": new_entry.serialize(),
            "message": f"{data['title']} added to entries."
        }
        return (jsonify(response), 201)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/entries', methods=['GET'])
def get_all_entries():

    response = {
        "entries": [entry.serialize() for entry in Entry.get_all()]
    }
    return jsonify(response)

# -------------------------------------------------------------------


@ app.route('/entries/<entry_id>', methods=['GET'])
def get_entry(entry_id):

    entry = Entry.get_by_id(entry_id)

    if entry != None:
        response = {
            "entry": entry.serialize()
        }
        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no entry with id {entry_id}."
        }
        return (jsonify(response), 404)

# -------------------------------------------------------------------


@app.route('/entries/<entry_id>', methods=['PATCH', 'PUT'])
@api_key_required
def update_entry(entry_id):

    entry = Entry.get_by_id(entry_id)
    if entry == None:
        response = {
            "status": "not found",
            "message": f"There is no entry with id {entry_id}."
        }
        return (jsonify(response), 404)

    # validate form
    form = EntryForm()
    form.participant_id.choices = Participant.get_choices()
    form.country_id.choices = Country.get_choices()
    if form.validate():

        # prevent creation of duplicate resource
        country_id = request.json.get('country_id', None)
        year = request.json.get('year', None)
        existing_entry = Entry.get_by_props(country_id, year)

        if existing_entry != None and existing_entry.id != entry_id:
            response = {
                "status": "duplicate",
                "message": "An entry for this year and country already exists in the database.",
                "entry": existing_entry.serialize()
            }
            return jsonify(response)

        # update resource
        data = {k: v for k, v in request.json.items()}
        updated_entry = Entry.update(
            entry,
            data.get('participant_id', None),
            data.get('country_id', None),
            data.get('title', None),
            data.get('year', None),
            data.get('eurovision_resource_url', None),
            data.get('eurovision_video_url', None),
            data.get('music_video_url', None),
            data.get('spotify_url', None),
            data.get('written_by', None),
            data.get('composed_by', None),
            data.get('broadcaster', None),
            data.get('lyrics', None),
            data.get('lyrics_language', None),
            data.get('lyrics_english', None))

        response = {
            "status": "success",
            "entry": updated_entry.serialize(),
            "message": f"{updated_entry.title} updated."
        }
        return jsonify(response)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/entries/<entry_id>', methods=['DELETE'])
@api_key_required
def delete_entry(entry_id):

    entry = Entry.get_by_id(entry_id)
    if entry != None:

        status = Entry.delete(entry_id)
        if status == "deleted":
            response = {
                "deleted": entry_id,
                "status": "success",
                "message": f"Entry with id {entry_id} has been deleted."
            }

        else:
            response = {
                "status": "error",
                "message": f"There was an error deleting entry with id {entry_id}."
            }

        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no entry with id {entry_id}."
        }
        return (jsonify(response), 404)

#####################################################################
# ----------------------------- Events ---------------------------- #
#####################################################################


@ app.route('/events', methods=['POST'])
@api_key_required
def add_event():

    # validate form
    form = EventForm()
    form.type.choices = EVENT_TYPE_LIST
    form.host_country_id.choices = Country.get_choices()
    if form.validate():

        # prevent creation of duplicate resource
        event_name = request.json.get('event', None)
        type = request.json.get('type', None)
        year = request.json.get('year', None)
        existing_event = Event.get_by_props(event_name, type, year)

        if existing_event != None:
            response = {
                "status": "duplicate",
                "message": "An event with this name, type, and year already exists in the database.",
                "event": existing_event.serialize()
            }
            return jsonify(response)

        # create new resource
        data = {k: v for k, v in request.json.items()}

        new_event = Event.register(
            data.get("event", None),
            data.get("type", None),
            data.get("year", None),
            data.get("date", None),
            data.get("start_time", None),
            data.get("end_time", None),
            data.get("eurovision_resource_url", None),
            data.get("recap_video_url", None),
            data.get("video_playlist_url", None),
            data.get("spotify_playlist_url", None),
            data.get("host_city", None),
            data.get("host_country_id", None))

        response = {
            "status": "success",
            "event": new_event.serialize(),
            "message": f"{data['event']} added to events."
        }
        return (jsonify(response), 201)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/events', methods=['GET'])
def get_all_events():

    response = {
        "events": [event.serialize() for event in Event.get_all()]
    }
    return jsonify(response)

# -------------------------------------------------------------------


@ app.route('/events/<event_id>', methods=['GET'])
def get_event(event_id):

    event = Event.get_by_id(event_id)

    if event != None:
        response = {
            "event": event.serialize()
        }
        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no event with id {event_id}."
        }
        return (jsonify(response), 404)

# -------------------------------------------------------------------


@app.route('/events/<event_id>', methods=['PATCH', 'PUT'])
@api_key_required
def update_event(event_id):

    event = Event.get_by_id(event_id)
    if event == None:
        response = {
            "status": "not found",
            "message": f"There is no event with id {event_id}."
        }
        return (jsonify(response), 404)

    # validate form
    form = EventForm()
    form.type.choices = EVENT_TYPE_LIST
    form.host_country_id.choices = Country.get_choices()
    if form.validate():

        # prevent creation of duplicate resource
        event_name = request.json.get('event', None)
        type = request.json.get('type', None)
        year = request.json.get('year', None)
        existing_event = Event.get_by_props(event_name, type, year)

        if existing_event != None and existing_event.id != event_id:
            response = {
                "status": "duplicate",
                "message": "An event with this name, type, and year already exists in the database.",
                "event": existing_event.serialize()
            }
            return jsonify(response)

        # update resource
        data = {k: v for k, v in request.json.items()}
        updated_event = Event.update(
            event,
            data.get('event', None),
            data.get('type', None),
            data.get('year', None),
            data.get('date', None),
            data.get('start_time', None),
            data.get('end_time', None),
            data.get('eurovision_resource_url', None),
            data.get('recap_video_url', None),
            data.get('video_playlist_url', None),
            data.get('spotify_playlist_url', None),
            data.get('host_city', None),
            data.get('host_country_id', None))

        response = {
            "status": "success",
            "event": updated_event.serialize(),
            "message": f"{updated_event.event} updated."
        }
        return jsonify(response)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/events/<event_id>', methods=['DELETE'])
@api_key_required
def delete_event(event_id):

    event = Event.get_by_id(event_id)
    if event != None:

        status = Event.delete(event_id)
        if status == "deleted":
            response = {
                "deleted": event_id,
                "status": "success",
                "message": f"Event with id {event_id} has been deleted."
            }

        else:
            response = {
                "status": "error",
                "message": f"There was an error deleting event with id {event_id}."
            }

        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no event with id {event_id}."
        }
        return (jsonify(response), 404)

#####################################################################
# --------------- Performances / Events-Entries ------------------- #
#####################################################################


@ app.route('/performances', methods=['POST'])
@api_key_required
def add_performance():

    # validate form
    form = EventEntryForm()
    form.event_id.choices = Event.get_choices()
    form.entry_id.choices = Entry.get_choices()
    form.qualified.choices = [('true', 'Yes'), ('false', 'No')]
    if form.validate():

        # prevent creation of duplicate resource
        event_id = request.json.get('event_id', None)
        entry_id = request.json.get('entry_id', None)
        existing_performance = Event_Entry.get_by_ids(event_id, entry_id)

        if existing_performance != None:
            response = {
                "status": "duplicate",
                "message": "A performance with this entry and event already exists in the database.",
                "performance": existing_performance.serialize()
            }
            return jsonify(response)

        # create new resource
        data = {k: v for k, v in request.json.items()}
        new_performance = Event_Entry.register(
            data.get('event_id', None),
            data.get('entry_id', None),
            data.get('points', None),
            data.get('place', None),
            data.get('qualified', None),
            data.get('running_order', None))

        response = {
            "status": "success",
            "performance": new_performance.serialize(),
            "message": "Performance added to database."
        }
        return (jsonify(response), 201)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/performances', methods=['GET'])
def get_all_performances():

    response = {
        "performances": [performance.serialize() for performance in Event_Entry.get_all()]
    }
    return jsonify(response)

# -------------------------------------------------------------------


@ app.route('/performances/<performance_id>', methods=['GET'])
def get_performance(performance_id):

    performance = Event_Entry.get_by_id(performance_id)

    if performance != None:
        response = {
            "performance": performance.serialize()
        }
        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no performance with id {performance_id}."
        }
        return (jsonify(response), 404)

# -------------------------------------------------------------------


@app.route('/performances/<performance_id>', methods=['PATCH', 'PUT'])
@api_key_required
def update_performance(performance_id):

    performance = Event_Entry.get_by_id(performance_id)
    if performance == None:
        response = {
            "status": "not found",
            "message": f"There is no performance with id {performance_id}."
        }
        return (jsonify(response), 404)

    # validate form
    form = EventEntryForm()
    form.event_id.choices = Event.get_choices()
    form.entry_id.choices = Entry.get_choices()
    form.qualified.choices = [('true', 'Yes'), ('false', 'No')]
    if form.validate():

        # prevent creation of duplicate resource
        event_id = request.json.get('event_id', None)
        entry_id = request.json.get('entry_id', None)
        existing_performance = Event_Entry.get_by_ids(event_id, entry_id)

        if existing_performance != None and existing_performance.id != performance_id:
            response = {
                "status": "duplicate",
                "message": "A performance with this entry and event already exists in the database.",
                "performance": existing_performance.serialize()
            }
            return jsonify(response)

        # update resource
        data = {k: v for k, v in request.json.items()}
        updated_performance = Event_Entry.update(
            performance,
            data.get('event_id', None),
            data.get('entry_id', None),
            data.get('points', None),
            data.get('place', None),
            data.get('qualified', None),
            data.get('running_order', None))

        response = {
            "status": "success",
            "performance": updated_performance.serialize(),
            "message": f"{updated_performance.id} updated."
        }
        return jsonify(response)

    # return errors if form does not validate
    else:
        return (jsonify({"errors": form.errors}), 400)

# -------------------------------------------------------------------


@ app.route('/performances/<performance_id>', methods=['DELETE'])
@api_key_required
def delete_performance(performance_id):

    performance = Event_Entry.get_by_id(performance_id)
    if performance != None:

        status = Event_Entry.delete(performance_id)
        if status == "deleted":
            response = {
                "deleted": performance_id,
                "status": "success",
                "message": f"Performance with id {performance_id} has been deleted."
            }

        else:
            response = {
                "status": "error",
                "message": f"There was an error deleting performance with id {performance_id}."
            }

        return jsonify(response)

    else:
        response = {
            "status": "not found",
            "message": f"There is no performance with id {performance_id}."
        }
        return (jsonify(response), 404)
