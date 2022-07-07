# -*- coding: UTF-8 -*
from modules.profiles.models import Country

def NormalizerHer(herencia):
	_nherencia = []
	for _user in herencia:
		_country = get_country(_user[10])
		_last = get_country(_user[11])
		tmp_user = {"user_id":_user[0], "username":_user[1], "balance":_user[2], "session":_user[3], "coin":_user[4], "create_agent":_user[5], "last_login":_user[6], "is_active":_user[7], "boss":_user[8], "email":_user[9], "country":_country, "last_ip":_last, "register_date":_user[12], "last_ips":_user[13]}
		_nherencia.append(tmp_user)

	return _nherencia

def NormalizerUser(_user_list):
	try:
		_user = _user_list[0]
		_country = get_country(_user[10])
		_last = get_country(_user[11])
		return {"user_id":_user[0], "username":_user[1], "balance":_user[2], "session":_user[3], "coin":_user[4], "create_agent":_user[5], "last_login":_user[6], "is_active":_user[7], "boss":_user[8], "email":_user[9], "country":_country, "last_ip":_last, "register_date":_user[12], "last_ips":_user[13]}
	except:
		_user = _user_list
		_country = get_country(_user[10])
		_last = get_country(_user[11])
		return {"user_id":_user[0], "username":_user[1], "balance":_user[2], "session":_user[3], "coin":_user[4], "create_agent":_user[5], "last_login":_user[6], "is_active":_user[7], "boss":_user[8], "email":_user[9], "country":_country, "last_ip":_last, "register_date":_user[12], "last_ips":_user[13]}

def get_country(country_id):
	_raw_country = Country.objects.filter(id=country_id).values_list("name")
	if _raw_country.exists():
		return _raw_country[0]
	else:
		return "None"