# -*- coding: UTF-8 -*
from django.contrib.auth.models import User
from modules.profiles.models import UserToken
from datetime import datetime
import hashlib

def check_user_token(_user):
	_user_token = UserToken.objects.filter(user=_user)

	if not _user_token.exists():
		return {'status':False}
	else:
		return {'status':True, 'token':_user_token[0].token}

def gen_token(_user):
	created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	part_token = "%d%s%s" % (_user.pk, _user.username, str(created_date))
	_token = hashlib.sha1(part_token).hexdigest()
	return {'token':_token}

def get_user_token(user_id):
	_token = UserToken.objects.filter(user=user_id)
	if not _token.exists():
		return {'status':False}
	else:
		return {'status':True, 'token':_token[0].token}

def new_user_token(user_id):
	
	_user = User.objects.get(pk=user_id)
	_try_token = check_user_token(_user)
	if _try_token['status']:
		return {'status':True, 'token':_try_token['token']}

	_token = gen_token(_user)
	_user_token = UserToken(user=_user, token=_token['token'])
	_user_token.save()
	return {'status':True, 'token':_token['token']}

def get_user_by_token(_token):
	_token = UserToken.objects.filter(token=_token)
	if not _token.exists():
		return False
	return int(_token[0].user_id)