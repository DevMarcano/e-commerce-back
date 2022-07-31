from django.conf import settings
from django.http import JsonResponse
from .models import Skin
from modules.core.login_decorateds import AuthToken, GetMethod, NewApiToken
from django.views.decorators.csrf import csrf_exempt
from modules.core.extras import get_profile_by_user, clean_domain
import json
import re


@csrf_exempt
@NewApiToken
def get_all_skins(request):
	all_skins = Skin.objects.filter(status=True).values_list('nombre_plataforma', 'domain', 'logo_plataforma', 'banner', )
	tmp_skins = []
	for skin in all_skins:
		tmp_dict = {'name':skin[0], 'domain':skin[1], 'logo':skin[2], 'banner':skin[3]}
		tmp_skins.append(tmp_dict)

	return JsonResponse({"skins":tmp_skins}, status=200)


@csrf_exempt
@NewApiToken
def get_in_skin(request):
	_clean_url = clean_domain(request.get_host())
	platf = Skin.objects.filter(domain=_clean_url,status=True).values_list('nombre_plataforma', 'domain', 'logo_plataforma', 'banner', 'cashier_id')
	if not platf.exists():
		return JsonResponse({'status':"False4"}, status=403)

	_skin = platf[0]
	try:
		_banners = _skin[3].replace('\'', '"')
		_banners = _banners.replace('u"', '"')
		_banners = json.loads(_banners)
	except:
		_banners = {}

	cash_prof = get_profile_by_user(int(_skin[4]))

	_raw_skin = {'name':_skin[0], 'domain':_skin[1], 'logo':_skin[2], 'banner':_banners, 'coin':str(cash_prof.coin.cod)}

	return JsonResponse(_raw_skin, status=200)