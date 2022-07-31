# -*- coding: UTF-8 -*
import functools
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.conf import settings
from django.contrib.auth.models import User
from .extras import ValidatedToken, check_pre_login, clean_domain
from modules.profiles.models import Profile, SessionToken
from .cryptography import encoded_params, encoded_dict, make_hash, verify_hash
import json
import time
from django.core.cache import cache

from operator import itemgetter


def timed(f):
	@functools.wraps(f)
	def wrapper(*args, **kwds):
		start = time.time()
		result = f(*args, **kwds)
		elapsed = time.time() - start
		return result
	return wrapper


def NewApiToken(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):

		if request.method != "POST":
			response = JsonResponse({'status':False, "message":"Method not allowed."}, status=403)
			return response
		
		public_key = settings.NEW_API_PUBLIC
		remote_token = request.META.get('HTTP_APITOKEN')
		if remote_token is None:
			return JsonResponse({'status':False,'message':'Unauthorized1'}, status=401)

		cache_key = str(remote_token)
		cache_time = 180

		#if cache.get(cache_key):
		#	return JsonResponse({'status':False, "message":"Unauthorizedhh"}, status=401)


		try:
			_raw_json = json.loads(request.body)
			_time = int(_raw_json['timestamp'])
		except:
			return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)

		_now_time = int(time.time())

		_restart_time = _now_time - _time

		#if _restart_time > 1:
		#	return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)

		_new_json = ""

		_final = len(_raw_json)
		count = 0
		
		for k, v in sorted(_raw_json.items(), key=itemgetter(0)):
			count += 1
			if count == _final:
				_new_json += "%s=%s" %(k, v)
			else:
				_new_json += "%s=%s&" %(k, v)

		#body = encoded_dict(json.loads(request.body))

		if not verify_hash(remote_token, _new_json, public_key):
			return JsonResponse({'status':False,'message':'Invalid Signature'}, status=401)

		cache.set(cache_key, "apitoken", cache_time)

		return f(request, *args, **kws)

	return decorated_function


def AuthToken(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		#if not request.user.is_anonymous():
		#	return f(request, *args, **kws)

		_clean_url = clean_domain(request.get_host())
			
		r_token = request.META.get('HTTP_AUTHORIZATION')
		if r_token is None:
			return JsonResponse({'status':False,'message':'Unauthorized'}, status=401)

		token_format = ValidatedToken(r_token)

		if not token_format['status']:
			return JsonResponse({'status':False,'message':token_format['message']}, status=401)

		_is_token_valid = check_pre_login(r_token, _clean_url)
		if not _is_token_valid['status']:
			return JsonResponse({'status':False,'message':_is_token_valid['message']}, status=401)

		_user = User.objects.get(id=_is_token_valid['user'])

		if not _user.is_active:
			return JsonResponse({'status':False,'message':'Unactived User'}, status=401)

		act_profs = Profile.objects.filter(user=_user)
		if not act_profs.exists():
			return JsonResponse({'status':False,'message':'Not User Profile'}, status=401)

		act_prof = act_profs[0]
		if not act_prof.status:
			try:
				_session_token = SessionToken.objects.get(token=_r_token)
				_session_token.delete()
			except:
				pass

			return JsonResponse({'status':False,'message':'Not User session'}, status=401)

		login(request, _user, backend=settings.AUTHENTICATION_BACKENDS[0])

		return f(request, *args, **kws)

	return decorated_function


def PostMethod(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		if request.method != "POST":
			response = JsonResponse({'status':False, "message":"Method not allowed."}, status=403)
			return response
		return f(request, *args, **kws)

	return decorated_function

def GetMethod(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		if request.method != "GET":
			return JsonResponse({'status':False, "message":"Method not allowed."}, status=403)
		return f(request, *args, **kws)

	return decorated_function

def CBMethod(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		_clean_url = clean_domain(request.get_host())
		platfs = ProfileSkin.objects.filter(domain=_clean_url)

		if not str(request.user.username) in ['PoweredBet'] and platfs[0].cashier.username != str(request.user.username):
			return JsonResponse({'status':False, "message":"Unauthorized"}, status=401)

		#_perms = ["Poweredbet"]
		#if not settings.DEBUG:
		#	if not str(request.user.username)[2:] in _perms:
		#		return JsonResponse({'status':False, "message":"Unauthorized"}, status=401)
		#else:
		#	if not str(request.user.username) in _perms:
		#		return JsonResponse({'status':False, "message":"Unauthorized"}, status=401)
		return f(request, *args, **kws)
	return decorated_function


def DebugON(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		if settings.DEBUG:
			return JsonResponse({'status':False, "message":"Unauthorized"}, status=401)
		return f(request, *args, **kws)
	return decorated_function


def ADLock(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		cache_key = str(request.user.pk) + str(request.build_absolute_uri())
		cache_time = 15
		if cache.get(cache_key):
			return JsonResponse({'status':False, "message":"Please try again in a moment"}, status=401)
		cache.set(cache_key, "Unauthorized", cache_time)
		return f(request, *args, **kws)

	return decorated_function


def BlockMT(f):
	@functools.wraps(f)
	def decorated_function(request, *args, **kws):
		cache_key = str(request.build_absolute_uri())
		cache_time = 2
		if cache.get(cache_key):
			return JsonResponse({'status':False, "message":"Unauthorized"}, status=401)
		cache.set(cache_key, "hola", cache_time)
		return f(request, *args, **kws)

	return decorated_function
