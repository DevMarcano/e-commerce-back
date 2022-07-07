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

class SlotExch(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)

class LuckySpinGS(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)
	id_game = StringField(required=True)

class EzugiToken(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)
	date = DateTimeField(default=datetime.datetime.utcnow)


class CityGames(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)

class Kalamba(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)

class Web3Transactions(Document):
	user_id = IntField(required=True)
	tx_hash = StringField(required=True)
	amount = DecimalField(required=True, precision=6)
	date = DateTimeField(default=datetime.datetime.utcnow)
	status = IntField(default=0)
	local_id = IntField(required=True)
	coin_id = StringField(required=True)
	skin_id = IntField(required=True)

class PlaysInfo(Document):
	user_id = IntField(required=True)
	play_id = StringField(required=True)
	info = StringField(required=True)
	date = DateTimeField(default=datetime.datetime.utcnow)
	order_number = StringField(required=True)
	bet_status = IntField(required=True) #0=CR_|1=DE_|2=RB_

class OneTouch(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)

class BetConnections(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)



class DragonGaming(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)
	
class UrgentGames(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)

class RevolverGames(Document):
	user_id = IntField(required=True)
	token = StringField(required=True)
	channel = IntField(required=True) #1 or 0