from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import Profile, SessionToken, RecoveryPass
from modules.skin.models import Skin
from modules.core.login_decorateds import AuthToken, GetMethod, NewApiToken, CBMethod, ADLock
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from modules.core.extras import ValidatedPass, get_profile_by_user, close, new_token, gen_token, check_date, all_countries, GetCountry, clean_domain, ValidatedEmail, ValidatedUsername, refresh_token, percent_rollover, userSerializer
from modules.core.tasks import UpdateProfile
from django.contrib.auth import login, authenticate, logout
import json

@csrf_exempt
@NewApiToken
def register_user(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)

	try:
		_password = json_data['password']
		_email = json_data['email']
		_username = json_data['username']
		#_domain = json_data['domain']
		#_country_id = int(json_data['country'])
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status':False, 'message':'No se encuentra la skin'}, status=403)
	_prefix = str(platfs[0].prefijo)
	
	_check_username = ValidatedUsername(_username)

	if not _check_username['status']:
		return JsonResponse({'status':False, 'message':_check_username['message']}, status=403)

	if not ValidatedEmail(_email)['status']:
		return JsonResponse({'status':False, 'message':'Invalid Email'}, status=403)

	try_mail = User.objects.filter(email=_email)
	if try_mail.exists():
		for _try_user in try_mail:
			if str(_try_user)[:2] == _prefix:
				return JsonResponse({'status':False, 'message':'Email already in use'}, status=403)

	_check_pass = ValidatedPass(_password)
	if not _check_pass['status']:
		return JsonResponse({'status':False, 'message':_check_pass['message']}, status=403)

	_username = "%s%s"%(_prefix, _username)
	
	try:
		_user = User.objects.create_user(username=_username,email=_email,password=_password)
		_user.save()
	except:
		return JsonResponse({'status':False, 'message':'username already in use'}, status=403)

	#_group = Group.objects.get(name='Customer')

	#_group.user_set.add(_user)

	#_clean_url = clean_domain(request.get_host())

	_prof_user = Profile.objects.create(user=_user, status=False, balance=0.00, skin_id=platfs[0].id)
	
	_prof_user.status = True
	
	_prof_user.save()
	
	UpdateProfile.delay(_user.pk)

	if _prof_user.status:
		_auth_token = refresh_token(_user, _clean_url)
	else:
		_auth_token = new_token(_user, _clean_url)
		
	return JsonResponse({'status':True, 'auth_token':_auth_token['token']})


@csrf_exempt
@NewApiToken
def login_user(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)

	try:
		_username = json_data['username']
		_password = json_data['password']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)

	_clean_url ="localhost:8000" #clean_domain(request.get_host())  #
	platf = Skin.objects.get(domain=_clean_url ,status=True)# cambiar _clean_url
	_prefix = str(platf.prefijo)
	
	_raw_user = User.objects.filter(username=_username)
	if not _raw_user.exists():
		_username = "%s%s" % (_prefix, _username)
	
	user = authenticate(username=_username, password=_password)
	if user is None:
		return JsonResponse({'status':False, "message":"Usuario o contraseña incorrectos"}, status=403)

	if not user.is_active:
		return JsonResponse({'status':False, "message":"El usuario esta bloqueado"}, status=403)

	ProfActive = get_profile_by_user(user.pk)

	#_ip = "190.200.52.5" #get_client_ip(request)[0] # 
	#log = open("profilesip.log", "a")
	#log.write(str({"Error":0, "menssage":"get_client_ip() ip del usuario al logear","ip":_ip}) + "\r\n")
	#try_country = GetCountry(_ip) 
	#log.write(str({"Error":0, "try_country":try_country}) + "\r\n")
	
	#if try_country:
	#	_last_country = try_country['country_id']
	#else:
	#	_last_country = 0

	#if(ProfActive.country_id == 0) or (ProfActive.country_id == 1) :
	#	if ProfActive.country_id != try_country:
	#		log.write(str({"Error":0, "Antiguo":ProfActive.country_id,"Nuevo":try_country}) + "\r\n")
	#		ProfActive.country_id = _last_country
	#		userip = RegistroIP.objects.filter(user_id=user.pk)
	#		if len(userip) == 0:
	#			RegistroIP.objects.create(user_id=user.pk, ip=_ip)
	#		else:
	#			userip[0].ip = _ip
	#			userip[0].save()
	#log.write("----------------------------" + "\r\n")
	#log.close()
	
	
	ProfActive.status = True
	#ProfActive.last_ips = _ip
	#ProfActive.last_ip = _last_country
	ProfActive.save()
	
	#HistoryLogedIp.objects.create(user_id=user.pk,ip=_ip)

	UpdateProfile.delay(user.pk)

	if ProfActive.status:
		_auth_token = refresh_token(user, _clean_url)
	else:
		_auth_token = new_token(user, _clean_url)
		
	return JsonResponse({'status':True, 'auth_token':_auth_token['token']})#, 'Group':actgroup

@csrf_exempt
@NewApiToken
@AuthToken
def close_session(request):
	#try_token = DeleteCFM(int(request.user.pk))
	#if not try_token:
	#	pass
	close(request)
	_r_token = request.META.get('HTTP_AUTHORIZATION')
	try:
		_session_token = SessionToken.objects.get(token=_r_token)
		_session_token.delete()
	except:
		pass
	return JsonResponse({'status':True}, status=200)

# Create your views here.

@csrf_exempt
@NewApiToken
@AuthToken
def get_user(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)
	try:
		_username = json_data['username']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url ="localhost:8000" #clean_domain(request.get_host())  #
	platf = Skin.objects.get(domain=_clean_url ,status=True)# cambiar _clean_url
	_prefix = str(platf.prefijo)	
	
	_user = User.objects.filter(username=_prefix+_username)
	if not _user.exists():
		return JsonResponse({'status':False, 'message':'Username not found'}, status=403)
	
	try:
		_profile = Profile.objects.get(user=_user[0].pk)
	except:
		return JsonResponse({'status':False, 'message':'Profile not found'}, status=403)
	
	return JsonResponse({'Status': True, 'User': userSerializer(_user[0]) , "profile": _profile.serialize()}, status=200)


@csrf_exempt
@NewApiToken
@AuthToken
def get_users(request):
	_clean_url = "localhost:8000" #clean_domain(request.get_host())
	try:
		platfs = Skin.objects.get(domain=_clean_url,status=True)#cambiar
	except:
		return JsonResponse({'status':False, 'message':'Platform not found'}, status=403)
	listuser = []
	profiles = Profile.objects.filter(skin_id=platfs.id)
	for prof in profiles:
		_user = User.objects.filter(id=prof.user_id)
		listuser.append({"user": userSerializer(_user[0]) , "profile": prof.serialize()})

	return JsonResponse({'status':True, 'user': listuser}, status=200)



@csrf_exempt
@NewApiToken
def pre_recovery(request):
	try:
		json_data = json.loads(request.body)
	except:
		response = JsonResponse({'status':False, "message":"Invalid request"}, status=403)
		return response

	try:
		email = json_data['email']
		#_domain = json_data['domain']
	except KeyError:
		response = JsonResponse({'status':False, "message":"Invalid request"}, status=403)
		return response

	if not ValidatedEmail(email)['status']:
		response = JsonResponse({'status':False, "message":"Invalid email"}, status=403)
		return response

	_domain = clean_domain(request.get_host())

	plat = Skin.objects.get(domain=_domain,status=True)#cambiar
	_prefix = str(plat.prefijo)

	_rec_users = User.objects.filter(email=email)
	if not _rec_users.exists():
		return JsonResponse({'status':False, "message":"Invalid Username"})
	if _rec_users > 1:
		for _user in _rec_users:
			if str(_user.username[:2]) == _prefix:
				_email_user = _user
	else:
		_email_user = _rec_users[0]
	

	_rec_token = gen_token(_email_user)

	_check_pass = RecoveryPass.objects.filter(user=_email_user)
	if _check_pass.exists():
		_check_p = _check_pass[0]
		_check_p.delete()

	_raw_token = RecoveryPass.objects.create(user=_email_user, created_date=_rec_token['date'], token=_rec_token['token'])

	_title = "Your requested password recovery token!"

	_rec_domain = "https://%s/recover/%s"%(_domain, _rec_token['token'])

	_demo = ["rgtbet.com", "rgtdemo.com"]

	
	#_raw_html = render_to_string('forgot-password.html')
	#_raw_html = _raw_html.replace('[logo]', plat.logo_plataforma)		
	#_raw_html = _raw_html.replace('[pageUrl]', "https://"+plat.domain)
	
	#_raw_html = _raw_html.replace('[TOKEN]', _rec_domain)
	#_raw_html = _raw_html.replace('[userName]', _user.username)
	#_send_email.delay([_email_user.email], _title, _raw_html, False)

	return JsonResponse({'status':True, "message":"A Recovery Code was sent to your Email."})


@csrf_exempt
@NewApiToken
def recovery_password(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':"False0"}, status=403)

	try:
		recovery_token = json_data['recovery_token']
		_new_password = json_data['new_password']
	except:
		return JsonResponse({'status':False}, status=403)

	_raw_token = RecoveryPass.objects.filter(token=recovery_token)
	if not _raw_token.exists():
		return JsonResponse({'status':False, "message":"Invalid or expired token 1"}, status=401)

	if check_date(_raw_token[0].created_date)['status']:
		_raw_token.delete()
		return JsonResponse({'status':False, "message":"Invalid or expired token"}, status=401)

	act_prof = get_profile_by_user(_raw_token[0].user.pk)

	act_user = act_prof.user

	#act_user = User.objects.get(username=_username)
	act_user.set_password(_new_password)
	act_user.save()

	_title = "Your password has been succesfully changed!"

	_domain = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_domain,status=True)#cambiar


	#_raw_html = render_to_string('reset-password.html')
	#_raw_html = _raw_html.replace('[logo]', platfs[0].logo_plataforma)		
	#_raw_html = _raw_html.replace('[pageUrl]', "https://"+platfs[0].domain)
	#_raw_html = _raw_html.replace('[coin]', act_prof.coin.name)


	# _send_email.delay([act_user.email], _title, _raw_html)

	return JsonResponse({'status':True, 'message':'Your password has been succesfully changed!'}, status=200)


@csrf_exempt
@NewApiToken
@AuthToken
def ChancePassword(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':"False2"}, status=403)

	try:
		old_password = str(json_data['pass'])
		password1 = str(json_data['pass1'])
		password2 = str(json_data['pass2'])
	except:
		return JsonResponse({'status':False}, status=403)

	if password1 != password2:
		return JsonResponse({'status':False}, status=403)

	_user = request.user

	if not _user.check_password(old_password):
		return JsonResponse({'status':False , 'message': 'Las contraseña anterior no coincid'}, status=403)

	if old_password == password1:
		return JsonResponse({'status':False , 'message' : 'Las contraseñas no coinciden'}, status=403)

	_user.set_password(password1)
	_user.save()

	return JsonResponse({'status':True}, status=200)