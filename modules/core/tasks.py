# -*- coding: UTF-8 -*
from django.conf import settings
from Casino.celery import app
from django.core.mail import send_mail, EmailMessage
from extras import get_profile_by_user, ZHbyCoin, clean_domain, check_bonus, can_bonus
from modules.games.GamesCache import CashierAllGames, GetFavs
from modules.plays.raw_querys import _update_balance, new_update
from modules.plays.models import GameBet,  PayBonus
import pytz
from modules.games.GamesCache import GetBetCache
from modules.profiles.helper import create_referral_code, calc_percent
from modules.core.UserToken import new_user_token
from modules.games.models import Provider
from datetime import datetime, timedelta
from modules.profiles.models import Alert
from modules.games.GamesCache import SetBetCache
import xlsxwriter
from modules.plays.helper_reports import totales, SortedDate, GenNewReport, SortedList, create_signature, GenNewHis, format_date, sort_head, calc_name, sort_her
from time import sleep
import requests
import json
from modules.core.new_herencia import GetAll, CacheProfile, CacheGroup
from modules.core.mongo_models import CbetBal, PlaysInfo
from django.template.loader import render_to_string
from modules.plataform.transactions import transaction_to_user
from modules.core.CoinConverter import fiat_usd, btc_usd
from modules.profiles.Skins import get_skin_email
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
	print msg.send()
	#if not settings.DEBUG:
	#	return msg.send()
	#else:
	#	return True

@app.task
def _send_email_atttach(to_list, _file):
	sender = settings.EMAIL_SENDER
	msg = EmailMessage(subject="Your requested report", body="", from_email=sender, to=to_list)
	msg.content_subtype = "html"
	msg.attach_file(_file)
	print msg.send()


@app.task
def create_referral(user_id):
	create_referral_code(user_id)

@app.task
def SetAllGames(_cashier, _opt, _country_id, _clean_url):
	CashierAllGames(_cashier, _opt, _country_id, _clean_url)

@app.task
def UpdateBalance(uid, amount_bet, amount_win):
	#_update_balance(uid, new_balance)
	return new_update(uid, amount_bet, amount_win)


@app.task
def UpdateProfile(uid):
	CacheProfile(uid, True)


@app.task
def InsertPlay(fecha, player_id, amount_bet, amount_pay, win_rate, id_bet, provider_id, saldo_anterior, saldo_posterior, game, uu_id, round_id=False):
	if round_id:
		date_now = datetime.today()#.strftime('%Y-%m-%d')
		date_before = date_now + timedelta(minutes=-60)
		#date_now = date_now.strftime('%Y-%m-%d') + " 23:59:59"
		#date_before = date_before.strftime('%Y-%m-%d') + " 00:00:01"
		_try_bets = GameBet.objects.filter(Q(date__range=(date_before, date_now))).filter(player_id=player_id, round_id=round_id, game=game)
		if _try_bets.exists():
			_try_bet = _try_bets[0]
			_try_bet.amount_bet = float(_try_bet.amount_bet) + amount_bet
			_try_bet.amount_win = float(_try_bet.amount_win) + amount_pay
			_try_bet.saldo_posterior = saldo_posterior
			_try_bet.save()
			_try_bet.win_rate = float(_try_bet.amount_bet) - float(_try_bet.amount_win)
			_try_bet.save()
		else:
			return GameBet.objects.create(uid=uu_id, date=fecha, player_id=player_id, amount_bet=amount_bet, amount_win=amount_pay, win_rate=win_rate, id_bet=str(id_bet), provider_id=provider_id, saldo_anterior=saldo_anterior, saldo_posterior=saldo_posterior, game=game, round_id=round_id)
	else:
		return GameBet.objects.create(uid=uu_id, date=fecha, player_id=player_id, amount_bet=amount_bet, amount_win=amount_pay, win_rate=win_rate, id_bet=str(id_bet), provider_id=provider_id, saldo_anterior=saldo_anterior, saldo_posterior=saldo_posterior, game=game)





@app.task
def RollBackPlay(ConProf, id_bet, prov):
	TryCancel = GetBetCache(id_bet)
	if not TryCancel:
		return {"status":False, "msg":"Transaction_not_exists", "error_code":-3}
	old_balance = 0.00
	new_balance = 0.00


	if prov.name in settings.MULTI_BET:
		if TryCancel['action'] != 0:
			if TryCancel['action'] != 2:
				result = {"status":False, "error_code":-1, "id_bet":TryCancel['gid']}
				return result
			else:
				result = {"status":False, "error_code":-2, "id_bet":TryCancel['gid']}
				return result


	_c_bet = GameBet.objects.get(uid=TryCancel['gid'])
	amount_rb = float(_c_bet.amount_bet) #* -1	

	r_bet = str(TryCancel['gid'])

	_up = UpdateBalance(ConProf.user.pk, 0.00, amount_rb)
	new_balance = _up['new_balance']
	old_balance = _up['old_balance']


	amount_win = float(_c_bet.amount_win) #* -1
	win_rate = float(_c_bet.win_rate) #* -1

	TryCancel['action'] = 2
	SetBetCache(TryCancel)
	_c_bet.amount_bet = 0.00
	_c_bet.win_rate = 0.00
	_c_bet.save()
	return {"status":True, "new_balance":new_balance, "old_balance":old_balance, "id_bet":r_bet}



@app.task
def RollBackPay(profile, id_bet, prov):
	TryCancel = GetBetCache(id_bet)
	if not TryCancel:
		return {"status": False, "msg": "Transaction_not_exists", "error_code": -1}

	amount = TryCancel["amount_pay"]

	r_bet = str(TryCancel["gid"])
	settlement_type = TryCancel["settlement_type"]
	if settlement_type == 0:
		value = amount
	else:
		value = -amount
	
	# settlement_type 0  --> + amount
	# settlement_type 1-6  --> - amount
	new_balances = UpdateBalance(profile.user.pk, 0.00, value)
	new_balance = new_balances['new_balance']
	old_balance = new_balances['old_balance']

	amount_bet = 0.00
	amount_win = 0.00
	win_rate = 0.00

	if amount < 0:
		amount = abs(amount)
		amount_bet = amount

	else:
		amount_win = amount

	win_rate = float(amount_bet) - float(amount_win)

	
	TryCancel['action'] = 3
	return {
		"status": True,
		"new_balance": new_balance,
		"old_balance": old_balance,
		"id_bet": r_bet,
		"cached_data": TryCancel
	}


@app.task
def RollSports(id_bet, prov_id, _act):
	_c_bets = GameBet.objects.filter(provider_id=prov_id,id_bet=id_bet)
	if not _c_bets.exists():
		return {"status":False, "msg":"", "error_code":-1}

	_c_bet = _c_bets[0]

	amount_rb = _c_bet.amount_bet
	r_bet = str(_c_bet.uid)

	ConProf = get_profile_by_user(int(_c_bet.player_id))

	old_balance = float(ConProf.balance)

	if _act == 0:
		new_balance = old_balance + float(amount_rb)
		UpdateBalance(ConProf.user.pk, 0.00, amount_rb)

	else:
		new_balance = old_balance - float(amount_rb)
		UpdateBalance(ConProf.user.pk, amount_rb, 0.00)


	
	_c_bet.amount_bet = 0.00
	_c_bet.save()
	return {"status":True, "new_balance":new_balance, "old_balance":old_balance, "id_bet":r_bet}


@app.task
def UpdateFavs(user_id):
	GetFavs(user_id, True)


#@app.task
#def UpdateAllHerencia(user_id):
#	UpdateGetHerencia(user_id)

@app.task
def gen_historial(_tipo, _user_list, _desde, _hasta, _to):
	_head = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
	_start_head = 0
	fecha_desde = format_date(_desde, 0)
	fecha_hasta = format_date(_hasta, 1)

	_sort = sort_head(_tipo)

	final_list = []

	for _user in _user_list:
		tmp_result = GenNewHis(_user, _tipo, fecha_desde, fecha_hasta)
		for _tr in tmp_result:
			final_list.append(_tr)

	raw_name = calc_name(str(_user_list))
	if settings.DEBUG:
		_name = '%s.xlsx'%(raw_name[:10])
	else:
		_name = '/tmp/%s.xlsx'%(raw_name[:10])
	#tmp_result = GenNewHis(_user_id, _tipo, fecha_desde, fecha_hasta)
	workbook = xlsxwriter.Workbook(_name)
	worksheet = workbook.add_worksheet()
	cell_format = workbook.add_format({'bold': True})
	worksheet.set_default_row(20)
	_start_count = 1

	_head_sheet = final_list[0]
	_sets = []
	for _s, _k in _sort.iteritems():
		if not _k in _sets:
			worksheet.write("%s%d"%(_head[_start_head], _start_count),_k, cell_format)
			_start_head += 1
			_sets.append(_k)

	#for k, v in _head_sheet.iteritems():
	#	worksheet.write("%s%d"%(_head[_start_head], _start_count),k)
	#	_start_head += 1

	_start_head = 0
	_start_count += 1
	_last = len(_sort) - 1
	_act = {0:"Deposit", 1:"Withdrawal", 2:"Referral Pay"}

	for _rd in final_list:
		#_rt['date'] = _rt['date'].replace(tzinfo=None)
		_rd['date'] = _rd['date'].strftime("%d-%m-%Y, %H:%M:%S.%f")
		try:
			_rd['action'] = _act[_rd['action']]
		except:
			pass
		try:
			_rd['tipo'] = _act[_rd['tipo']]
		except:
			pass
		for _s, _k in _sort.iteritems():
			try:
				worksheet.write("%s%d"%(_head[_start_head], _start_count), _rd[_s])
				_start_head += 1
			except:
				pass

		#worksheet.write("%s%d"%(_head[_start_head], _start_count), _sort[_start_head])
		#for k, v in _rd.iteritems():
		#	worksheet.write("%s%d"%(_head[_start_head], _start_count),v)
		#	_start_head += 1
		_start_head = 0
		_start_count += 1

	worksheet.set_column(0, _last, 25)

	workbook.close()

	if not settings.DEBUG:
		_send_email_atttach([_to], _name)


@app.task
def gen_herencia(user_id, _to):
	act_prof = get_profile_by_user(user_id)
	act_group = CacheGroup(act_prof.user)
	agents = []
	cashiers = []
	customers = []

	_sort = sort_her()

	#if act_group != "Admin":
	#	list_herencia = GetAllHerencia(user_id, act_group)
	#else:
	#	list_herencia = []


	if True:
		raw_name = calc_name(str(user_id))
		_name = '%s.xlsx'%(raw_name[:10])
		if act_group == "Cashier":
			list_herencia = GetAll(user_id, "Customer")
			workbook = xlsxwriter.Workbook(_name)
			workplayer = workbook.add_worksheet("Players")
			cell_format = workbook.add_format({'bold': True})
			workplayer.set_default_row(20)
			_head = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
			_start_head = 0
			_start_count = 1


			for _s, _k in _sort.iteritems():
				workplayer.write("%s%d"%(_head[_start_head], _start_count),_k, cell_format)
				_start_head += 1

			_start_head = 0
			_start_count += 1
			_last = len(_sort) - 1

			for _user in list_herencia:
				try:
					_user['last_login'] = _user['last_login']
				except:
					_user['last_login'] = "None"
				_user['register_date'] = _user['register_date']
				for _s, _k in _sort.iteritems():
					try:
						workplayer.write("%s%d"%(_head[_start_head], _start_count), _user[_s])
						_start_head += 1
					except:
						pass

				_start_head = 0
				_start_count += 1
			workplayer.set_column(0, _last, 25)
			workbook.close()

		else:
			_players = GetAll(user_id, "Customer")
			_cashiers = GetAll(user_id, "Cashier")
			_agents = GetAll(user_id, "Agent")
			_sheets_list = ["Players", "Cashiers", "Agents"]
			_start_sheet = 0
			workbook = xlsxwriter.Workbook(_name)
			cell_format = workbook.add_format({'bold': True})

			for _sheet in _sheets_list:
				worktemp = workbook.add_worksheet(_sheet)
				worktemp.set_default_row(20)
				_head = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
				_start_head = 0
				_start_count = 1
				for _s, _k in _sort.iteritems():
					worktemp.write("%s%d"%(_head[_start_head], _start_count),_k, cell_format)
					_start_head += 1

				_start_head = 0
				_start_count += 1
				_last = len(_sort) - 1

				for _user in list_herencia[_start_sheet]:
					try:
						_user['last_login'] = _user['last_login'].strftime("%d-%m-%Y, %H:%M:%S")
					except:
						_user['last_login'] = "None"
					try:
						_user['register_date'] = _user['register_date'].strftime("%d-%m-%Y, %H:%M:%S")
					except:
						_user['last_login'] = "None"
					for _s, _k in _sort.iteritems():
						try:
							worktemp.write("%s%d"%(_head[_start_head], _start_count), _user[_s])
							_start_head += 1
						except:
							pass
					_start_head = 0
					_start_count += 1
				_start_sheet += 1
				worktemp.set_column(0, _last, 25)
			workbook.close()
		#if not settings.DEBUG:
		_send_email_atttach([_to], _name)


@app.task
def check_alert(user_id, username, balance, coin, _domain):
	_ran = False
	_range_usd = [[100, 199], [200, 500], [500, 100000]]
	if coin == "mBTC":
		_amount_usd = btc_usd(balance)
	elif coin == "USD":
		_amount_usd = balance
	else:
		_amount_usd = fiat_usd(coin, balance)

	_check = Alert.objects.filter(player_id=user_id, status=0)

	if int(_amount_usd) in range(_range_usd[0][0], _range_usd[0][1]):
		_ran = 0

	elif int(_amount_usd) in range(_range_usd[1][0], _range_usd[1][1]):
		_ran = 1

	elif int(_amount_usd) in range(_range_usd[2][0], _range_usd[2][1]):
		_ran = 2

	else:
		return

	_email = get_skin_email(_domain)
	_dect = False

	_utc_now = datetime.utcnow()

	if _check.exists():
		for tmp_check in _check:
			_date = tmp_check.date
			_date = _date.replace(tzinfo=None)
			_diff = _utc_now - _date
			if _diff.days >= 7:
				tmp_check.status = 1
				tmp_check.save()
				_dect = True
		if _dect:
			Alert.objects.create(player_id=user_id, tier=_ran, date=_utc_now, status=0)
			if _email:
				mail_support("Customer: %s has a: %.2f Balance"%(username, balance), _email)

	else:
		Alert.objects.create(player_id=user_id, tier=_ran, date=_utc_now, status=0)
		if _email:
			mail_support("Customer: %s has a: %.2f Balance"%(username, balance), _email)

	return


@app.task
def get_bonus(user_id, provider_id, amount_bet, game_id):
	_can_bonus = check_bonus(user_id)
	if _can_bonus:
		_prov = Provider.objects.get(pk=provider_id)
		_bprovs = settings.BONUS_PROVS
		if _prov.name in _bprovs:
			if not str(game_id) in settings.BONUS_BAN:
				_bonus = PayBonus.objects.get(user_id=user_id)
				_bonus.rollover = float(_bonus.rollover) + amount_bet
				_bonus.save()
			else:
				pass


def local_task(task_id):
	result = AsyncResult(task_id)

	status = result.status

	if status != "SUCCESS":
		return False

	return result.result


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
			print _title

		return


@app.task
def save_playsInfo(user_id, play_id, raw_play, amount, PossibleWin, order_number, bet_status):
	#try:
	raw_bets = raw_play["Bets"][0]["BetStakes"]
	#except:
	#	return
	_bets = []
	_check_number = raw_play["CheckNumber"]
	_play = {"CheckNumber":_check_number, "Amount":amount, "PossibleWin":PossibleWin, "Bets":False}


	for rb in raw_bets:
		_dict_info = {"Event":rb["EventNameOnly"], "Tournament":rb["TournamentName"], "Date":rb["EventDateStr"], "Result":rb["FullStake"], "Teams":rb["Teams"], "TypeBet":rb["StakeTypeName"], "SportName":rb["SportName"], "ODDS":rb["Factor"]}
		_bets.append(_dict_info)

	_play["Bets"] = _bets
	#_dict_info = {"Event":raw_bets["EventNameOnly"], "Tournament":raw_bets["TournamentName"], "Date":raw_bets["EventDateStr"], "Result":raw_bets["FullStake"], "Teams":raw_bets["Teams"], "TypeBet":raw_bets["StakeTypeName"], "SportName":raw_bets["SportName"], "ODDS":raw_bets["Factor"], "Amount":amount, "PossibleWin":float(amount * raw_bets["Factor"]), "CheckNumber":_check_number}

	PlaysInfo.objects.create(user_id=user_id, play_id=play_id, info=str(_play), order_number=order_number, bet_status=bet_status)

	return



