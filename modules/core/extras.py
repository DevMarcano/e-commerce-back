# -*- coding: UTF-8 -*
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from modules.profiles.models import SessionToken, Profile
from datetime import datetime, timedelta
from calendar import monthrange
from django.core.cache import cache
import re
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
import hashlib
from django.contrib.auth import logout
from .mongo_models import Oldtokens
# from modules.plays.models import PayBonus, Transaction, CoinPayment
import pytz

def userSerializer(user):
	return{"Name": user.first_name, "last_name": user.last_name, "username":user.username[2:], "email": user.email, "lastLogin": user.last_login}


def CacheProfile(user_id, update=False):
	cache_time = 3600
	cache_key = str(user_id) + "_Profile"
	result = cache.get(cache_key)
	if result and not update:
		return result

	new_prof = list(Profile.objects.filter(user_id=user_id).values_list("user__pk", "user__username", "balance", "status", "user__email"))
	cache.set(cache_key, new_prof[0], cache_time)
	return new_prof[0]


def ZHbyCoin(coin_cod):
	coin_dict = {"VEF":90, "ARS":60, "BOB":145, "BRL":197, "BZD":81, "CLP":195, "COP":84, "CRC":98, "DOP":196, "GTQ":121, "HNL":208, "HTG":181, "MXN":161, "NIO":151, "PAB":177, "PEN":146, "PYG":74, "UYU":165, "USD":584, "EUR":584, "FUN":90, "mBTC":90, "TRY":223, "TND":222, "MM":584, "BDT":18}
	raw_zh = coin_dict[coin_cod]
	_zh = TimeZones.objects.filter(id=raw_zh)
	return _zh[0].name


def ValidatedEmail(email):
	if re.match("\A(?P<name>[\w\.\-_]+)@(?P<domain>[\w\-_]+).(?P<toplevel>[\w]+)\Z", email, re.IGNORECASE):
		return {'status':True}
	else:
		return {'status':False, 'message':'invalid email address'}


def ValidatedUsername(username):
	if len(username) > 12:
		return {'status':False, 'message':'invalid username len'}

	if re.match("^[a-zA-Z0-9]+$", username):
		return {'status':True}
	else:
		return {'status':False, 'message':'invalid username character'}


def ValidatedPass(password):
	if len(password) < 6 or len(password) > 42:
		return {'status':False, 'message':'password must have at least 6 characters 42 maximum'} #Corregir mensaje
	if not re.search("\d", password):
		return {'status':False, 'message':'Password must contain at least one number.'}
	if not re.search("[a-zA-Z]", password):
		return {'status':False, 'message':'Password must contain at least one letter.'}

	return {'status':True}


def ValidatedToken(_token):
	pattern = re.compile(r'\b[0-9a-f]{40}\b')
	if not bool(re.match(pattern, _token)):
		return {'status':False, 'message':'invalid token.'}

	return {'status':True}


def ValidatedIP(user_ip):
	ban_country = settings.BAN
	Geo = GeoIP2()
	try:
		UserCountry = Geo.country(user_ip)['country_code']
		if UserCountry in ban_country:
			return {'status':False, 'message':'ban Country'}

		return {'status':True}
	except:
		return {'status':True}


def GetCountry(_ip):
	Geo = GeoIP2()
	UserCountry = Geo.country(_ip)['country_code']

	if UserCountry is None:
		dict_country = {'country_code':"N/A", 'country_name':"N/A", 'country_id':0, 'ban':False}
		return dict_country

	_raw_countries = Country.objects.filter(code=UserCountry)
	if not _raw_countries.exists():
		return False

	_ban = False

	ban_country = settings.BAN_DEP
	if _raw_countries[0].name in ban_country:
		_ban = True

	dict_country = {'country_code':_raw_countries[0].code, 'country_name':_raw_countries[0].name, 'country_id':_raw_countries[0].pk, 'ban':_ban}
	return dict_country


def check_date(_token_date, expire_time=7200):
	_new_date = datetime.now()
	_new_date = _new_date.replace(tzinfo=None)
	_token_date = _token_date.replace(tzinfo=None)
	_minutes = _new_date - _token_date
	if int(_minutes.total_seconds()) >= expire_time:
		return {'status':True}

	return {'status':False}


def check_user_token(_user, _token=False):
	if not _token:
		_user_token = SessionToken.objects.filter(user=_user)
	else:
		_user_token = SessionToken.objects.filter(user=_user, token=_token)

	if not _user_token.exists():
		return {'status':False}
	_utk = _user_token[0]

	return {'status':True, 'token':_utk.token}


def check_pre_login(_token, _domain):
	_user_token = SessionToken.objects.filter(token=_token)
	if not _user_token.exists():
		return {'status':False, 'message':'invalid token'}
	_utk = _user_token[0]
	data = str(_utk.user.username) + str(_utk.created_date.strftime("%Y-%m-%d %H:%M:%S"))
	if hashlib.sha1(data.encode("utf-8")).hexdigest() != _utk.token:
		return {'status':False, 'message':'invalid token 2'}

	if _utk.domain != _domain:
		return {'status':False, 'message':'invalid domain session'}

	return {'status':True, 'user':_utk.user.id}


def gen_token(_user):
	created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	part_token = str(_user.username) + str(created_date)
	_token = hashlib.sha1(part_token.encode("utf-8")).hexdigest()
	return {'token':_token, 'date':created_date}


def new_token(_user, _domain):
	_try_token = check_user_token(_user)
	if _try_token['status']:
		return {'status':True, 'token':_try_token['token']}

	_token = gen_token(_user)
	_user_token = SessionToken(user=_user, token=_token['token'], created_date=_token['date'], domain=_domain)
	_user_token.save()
	if not settings.DEBUG:
		_old_token = Oldtokens(player_id=int(_user.pk), token=_token['token'])
		_old_token.save()
	return {'status':True, 'token':_token['token']}


def refresh_token(_user, _domain):
	try:
		_session_token = SessionToken.objects.get(user=_user)
		_session_token.delete()
	except:
		pass

	_token = gen_token(_user)
	_user_token = SessionToken(user=_user, token=_token['token'], created_date=_token['date'], domain=_domain)
	_user_token.save()
	if not settings.DEBUG:
		_old_token = Oldtokens(player_id=int(_user.pk), token=_token['token'])
		_old_token.save()
	return {'status':True, 'token':_token['token']}

def get_profile_by_user(uid):
	try:
		_prof = Profile.objects.get(user_id=uid)
		return _prof
	except:
		return False		


def close(request):
	act_prof = get_profile_by_user(request.user.pk)
	act_prof.status = 0
	act_prof.save()
	CacheProfile(request.user.pk, True)
	try:
		_session_token = SessionToken.objects.get(user=request.user)
		_session_token.delete()
	except:
		pass
	try:
		logout(request)
	except:
		pass


def all_countries():
	cache_key = "all_countries"
	cache_time = 60000
	result = cache.get(cache_key)
	if result:
		return result

	list_country = []
	_raw_countries = Country.objects.all()
	for _rc in _raw_countries:
		tmp_dict = {'country_code':_rc.code, 'country_name':_rc.name, 'country_id':_rc.pk}
		list_country.append(tmp_dict)

	cache.set(cache_key, list_country, cache_time)

	return list_country


def clean_domain(_domain):
	if _domain[:4] == "www.":
		_domain = _domain[4:]
	return _domain


def check_bonus(uid):
	_try_bonus = PayBonus.objects.filter(user_id=uid)
	if not _try_bonus.exists():
		return False

	_try_bonu = _try_bonus[0]

	_create = _try_bonu.date
	_create = _create.replace(tzinfo=None)
	_now = datetime.now()
	_now = _now.replace(tzinfo=None)
	_diff = _now - _create
	_month = _diff.days / 30
	_total_roll = float(_try_bonu.bonus_amount) * 40

	if float(_try_bonu.rollover) >= _total_roll:
		_try_bonu.delete()
		return False

	else:
		return True


def can_bonus(uid, _balance, _coin):
	_min_bal = 0.00

	if _coin == "mBTC":
		_min_bal = 5.00
	elif _coin == "USD":
		_min_bal = 50.00

	_deposits = Transaction.objects.filter(reciver_id=uid, action=0).exclude(memo="AutoBonus").count()

	
	#_deposits = CoinPayment.objects.filter(user_id=uid, tipo=0, status=1).count()
	_percent_dict = {1:100, 2:50, 3:35}

	_try_bonus = PayBonus.objects.filter(user_id=uid)
	if _try_bonus.exists() and _balance > _min_bal:
		return {'status':False}
		
	if _deposits == 0:
		return {'status':True, 'percent':_percent_dict[_deposits]}

	elif _deposits == 1 or _deposits == 2:
		return {'status':True, 'percent':_percent_dict[_deposits]}

	else:
		_deposits = 3
		return {'status':True, 'percent':_percent_dict[_deposits]}


def percent_rollover(uid):
	_try_bonus = PayBonus.objects.filter(user_id=uid)
	if not _try_bonus.exists():
		return False
	_try_bonu = _try_bonus[0]

	_total_roll = float(_try_bonu.bonus_amount) * 40
	act_roll = float(_try_bonu.rollover)

	if act_roll == 0:
		_percent = 0.00

	else:
		_percent = act_roll * 100 / _total_roll
		#_percent = _percent / _total_roll

	return {'total_rollover':_total_roll, 'current_rollover':act_roll, 'percent_rollover':_percent, 'status':True}


def clean_str(_string):
	return  re.sub('[^a-zA-Z0-9]','',_string)
