# -*- coding: UTF-8 -*
from django.conf import settings
from comercio.celery import app
from django.core.mail import send_mail, EmailMessage
from .extras import get_profile_by_user, ZHbyCoin, clean_domain, check_bonus, can_bonus, CacheProfile
#from modules.games.GamesCache import CashierAllGames, GetFavs
#from modules.plays.raw_querys import _update_balance, new_update
#from modules.plays.models import GameBet,  PayBonus
import pytz
#from modules.games.GamesCache import GetBetCache
#from modules.profiles.helper import create_referral_code, calc_percent
from modules.core.UserToken import new_user_token
#from modules.games.models import Provider
from datetime import datetime, timedelta
# from modules.profiles.models import Alert
#from modules.games.GamesCache import SetBetCache
from time import sleep
import requests
import json
from modules.core.mongo_models import CbetBal
from django.template.loader import render_to_string
#from modules.plataform.transactions import transaction_to_user
#from modules.core.CoinConverter import fiat_usd, btc_usd
#from modules.profiles.Skins import get_skin_email
from django.db.models import Q
from django.core.cache import cache

@app.task
def check_deposit(transaction_id, foreign_id):
	cache_key = "cp:%s-%s"%(transaction_id, foreign_id)
	if cache.get(cache_key):
		return True
	cache.set(cache_key, True, 43200)
	return False

@app.task
def mail_support(message, _to=False):
	sender = settings.EMAIL_SENDER
	if not _to:
		_to = settings.EMAIL_SUP
	subject = "Alert Notification"
	msg = EmailMessage(subject=subject, body=message, from_email=sender, to=_to)
	msg.send()

@app.task
def _new_user_token(user_id):
	new_user_token(user_id)

@app.task
def _send_email(to_list, subject, message, reply_to=False, sender=False):
	if not sender:
		sender = settings.EMAIL_SENDER
		
	if not reply_to:
		msg = EmailMessage(subject=subject, body=message, from_email=sender, to=to_list )
	else:
		msg = EmailMessage(subject=subject, body=message, from_email=sender, to=to_list, reply_to=reply_to)

	msg.content_subtype = "html"

@app.task
def _send_email_atttach(to_list, _file):
	sender = settings.EMAIL_SENDER
	msg = EmailMessage(subject="Your requested report", body="", from_email=sender, to=to_list)
	msg.content_subtype = "html"
	msg.attach_file(_file)
	print(msg.send())

#@app.task
#def UpdateBalance(uid, amount_bet, amount_win):
	#_update_balance(uid, new_balance)
#	return new_update(uid, amount_bet, amount_win)

@app.task
def UpdateProfile(uid):
	CacheProfile(uid, True)

# def local_task(task_id):
#	result = AsyncResult(task_id)
#
#	status = result.status
#
#	if status != "SUCCESS":
#		return False
#
#	return result.result


@app.task
def send_cbet(user_id, amount_bet):
	_amount_cbet = float(amount_bet * 0.1)
	if len(CbetBal.objects.filter(user_id=user_id)) == 0:
		_cb = CbetBal.objects.create(user_id=user_id, balance=0.00)

	_user_cbet = CbetBal.objects.filter(user_id=user_id)[0]

	_total = float(_user_cbet.balance) + float(_amount_cbet)
	_user_cbet.balance = _total
	_user_cbet.save()

	return

@app.task
def pay_bonus(user_id, _total, _old_balance, txn_id=False):
	act_prof = get_profile_by_user(user_id)
	act_boss = get_profile_by_user(act_prof.direct_boss.pk)
	_bonus = can_bonus(int(act_prof.user.pk), _old_balance, str(act_prof.coin.cod))
	if _bonus['status']:
		_mult = _bonus['percent']
		_per = calc_percent(_total, _mult)
		_memo = "AutoBonus"
		if txn_id:
			_memo = "%s|%s"%(_memo, txn_id)
		make_transfer = transaction_to_user(3, int(act_prof.user.pk), int(act_boss.user.pk), _per, _memo)
		if make_transfer["status"]:
			_old_bonus = PayBonus.objects.filter(user_id=int(act_prof.user.pk))
			if _old_bonus.exists():
				_old = _old_bonus[0]
				_old.delete()
			_pay_bonus = PayBonus.objects.create(user_id=int(act_prof.user.pk), bonus_amount=_per, rollover=0.00)

		if str(act_prof.coin.cod) == "mBTC":
			if _mult == 100:
				_free = 20
				_raw_html = render_to_string('20_free.html')
			elif _mult == 50:
				_free = 15
				_raw_html = render_to_string('15_free.html')
			else:
				_free = 10
				_raw_html = render_to_string('10_free.html')
		elif str(act_prof.coin.cod) == "USD":
			if _mult == 100:
				_free = 20
				_raw_html = render_to_string('20_free_1.html')
			elif _mult == 50:
				_free = 15
				_raw_html = render_to_string('15_free_1.html')
			else:
				_free = 10
				_raw_html = render_to_string('10_free_1.html')

		_title = "Here's your %s free spins"%(_free)
		if not settings.DEBUG:
			_send_email.delay([str(act_prof.user.email)], _title, _raw_html)
		else:
			print(_title)
		return