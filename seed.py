from models import db, Participant, Country, Event, Entry, Event_Entry
from app import app

db.drop_all()
db.create_all()
