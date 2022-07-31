# -*- coding: UTF-8 -*
from mongoengine import *
import datetime
from modules.profiles.models import Profile
from django.conf import settings

class Oldtokens(Document):
	connect(settings.M_DB, host=settings.M_HOST, port=int(settings.M_PORT), username=settings.M_USER, password=settings.M_PWD, authentication_source="admin")
	player_id = IntField(required=True)
	token = StringField(required=True)
	created_date = DateTimeField(default=datetime.datetime.utcnow)

class TokensMP(Document):
	csrfToken = StringField(required=True)
	user_id = IntField(required=True)
	date = DateTimeField(default=datetime.datetime.utcnow)
	email = StringField(required=True)
	token = StringField(required=True)

class CardsMP(Document):
	user_id = IntField(required=True)
	card = StringField(required=True)

class CbetBal(Document):
	user_id = IntField(required=True)
	balance = DecimalField(required=True, precision=6)

class RegistroIP(Document):
	user_id = IntField(required=True)
	ip = StringField(required=True)

class HistoryLogedIp(Document):
	user_id = IntField(required=True)
	ip = StringField(required=True)
	date = DateTimeField(default=datetime.datetime.utcnow)
