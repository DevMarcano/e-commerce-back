from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from models import Profile, SessionToken
from modules.skin.models import Skin
from modules.core.login_decorateds import AuthToken, GetMethod, BackView, NewApiToken, CBMethod, ADLock, LobbyView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from modules.core.extras import ValidatedPass, get_profile_by_user, close, new_token, gen_token, check_date, all_countries, GetCountry, clean_domain, ValidatedEmail, ValidatedUsername, refresh_token, percent_rollover
from modules.core.tasks import _send_email, UpdateProfile, create_referral, _new_user_token, gen_herencia
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

	_clean_url = clean_domain(request.get_host())

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

	_prof_user = Profile(user=_user, status=False)
	_prof_user.save()

	_prof_user.status = True

	_prof_user.skin = platfs[0].pk
	
	_prof_user.save()
	UpdateProfile.delay(_user.pk)

	if _prof_user.status:
		_auth_token = refresh_token(_user, _clean_url)
	else:
		_auth_token = new_token(_user, _clean_url)
		
	return JsonResponse({'status':True, 'auth_token':_auth_token['token'], 'Group':"Customer"})


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
		_username = "%s%s"%(_prefix, _username)

	if not request.user.is_anonymous():
		if request.user.username != _username:
			close(request)
			return JsonResponse({'status':False, 'message':'Please try again'}, status=403)
	
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

	#UpdateProfile.delay(user.pk)

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
