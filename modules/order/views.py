from django.http import JsonResponse
from modules.profiles.models import Profile
from modules.skin.models import Skin
from modules.core.login_decorateds import AuthToken, GetMethod, NewApiToken, CBMethod, ADLock, PostMethod
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from modules.products.models import Product, Provider, Category
from modules.order.models import Order, ProductsInOrder
from modules.core.extras import ValidatedPass, get_profile_by_user, close, new_token, gen_token, check_date, all_countries, GetCountry, clean_domain, ValidatedEmail, ValidatedUsername, refresh_token, percent_rollover
from modules.core.tasks import _send_email, UpdateProfile, _new_user_token
import json
import uuid
from django.db import connection as _db

@PostMethod
@csrf_exempt
def save_car(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)

	try:
		IdP = json_data['IdP']
		UserCar = json_data['user']
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)

	_user = User.objects.filter(id=UserCar)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	_car = Order.objects.filter(user=UserCar, skin_id=platfs[0].id, status=3)

	#if not _car.exists():
	#	try:
	orderid = uuid.uuid4()
	print(orderid)
	_newCar = Order.objects.create(order_uuid=str(orderid), user=int(UserCar), skin_id=platfs[0].id, total=0.00, status=3)
	_newCar.save()
	_car = _newCar
	#	except:
	#		return JsonResponse({'status': False, 'message': 'error ocurred creating order'}, status=403)
	#else:
	#	_car = _car[0]
	
	total=0
	_products = []
	for pro in IdP:
		print(pro)
		prod = Product.objects.get(id=pro["id"])
		if pro["Cant"] < prod.Cantidad:
			_newProdInCar = ProductsInOrder.objects.create(order=_car.order_uuid, products=prod.id, totalPro=prod.Precio*pro["Cant"], cant=pro["Cant"])
			_newProdInCar.save()
			total = total + (_newProdInCar.unit * _newProdInCar.cant)
			_products.append(_newProdInCar.Serialize())
		else:
			return JsonResponse({'status': False, 'message': 'Product '+ prod.Name + 'not disponible in stock '+ pro.Cantidad +' try cant lower'}, status=403)
	
	_car.total = total
	_car.save()
	
	return JsonResponse({'status': True, "Car": _car.Serialize(), "Products":_products}, status=200)


@PostMethod
@csrf_exempt
def cancel_car(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)

	try:
		_order = json_data['order']
		UserCar = json_data['User']
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	platfs = platfs[0]

	_user = User.objects.filter(id=UserCar)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)
	_user = _user[0]
	
	_car = Order.objects.filter(order_uuid=_order, user=UserCar, skin_id=platfs.id)
	if not _car.exists():
		return JsonResponse({'status': False, 'message': 'Car not found'}, status=403)
	_car = _car[0]

	#if _car.status != 1:
		#profile = Profile.objects.get(user=UserCar)
		#save historial de pagos como devolucion
		#profile.balance = profile.balance + _car.total

	_car.status = 2
	_car.save()

	return JsonResponse({'status': True, 'message': 'Orden Canceled Sussefull', 'car': _car.Serialize()}, status=200)	


@PostMethod
@csrf_exempt
def historyUser(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)

	try:
		UserCar = json_data['user']
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	platfs = platfs[0]
	
	_user = User.objects.filter(id=UserCar)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)
	_user = _user[0]

	_orders = Order.objects.filter(user=_user.id ,skin_id=platfs.id)
	if not _orders.exists():
		return JsonResponse({'status': False, 'message': 'Car not found'}, status=403)
	list_order=[]
	for order in _orders:
		_products = ProductsInOrder.objects.filter(order=order.order_uuid)
		list_prod = []
		for prod in _products:
			list_prod.append(prod.Serialize())
		list_order.append({"order":order.Serialize(), "products":list_prod})

	return JsonResponse({'status': True, "orders": list_order}, status=200)


@PostMethod
@csrf_exempt
def history(request):

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	platfs = platfs[0]
	
	_orders = Order.objects.filter(skin_id=platfs.id)
	if not _orders.exists():
		return JsonResponse({'status': False, 'message': 'Car not found'}, status=403)
	list_order=[]
	for order in _orders:
		_products = ProductsInOrder.objects.filter(order=order.order_uuid)
		list_prod = []
		for prod in _products:
			list_prod.append(prod.Serialize())
		list_order.append({"order":order.Serialize(), "products":list_prod})

	return JsonResponse({'status': True, "orders": list_order}, status=200)


@PostMethod
@csrf_exempt
def historyProvider(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)

	try:
		_provider = json_data['provider']
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000" #clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	platfs = platfs[0]
	
	provider = Provider.objects.filter(id=_provider)
	if not provider.exists():
		return JsonResponse({'status': False, 'message': 'Provider not exists'}, status=403)
	provider = provider[0]
	
	_cursor=_db.cursor()
	_sel = 	"select order_productsinorder.order, products_product.id, products_product.Name, order_productsinorder.cant, products_product.Precio, order_productsinorder.totalPro from products_product inner join order_productsinorder on (order_productsinorder.products in (select products_product.id from products_product where Prov_id = "+str(provider.id)+")) and order_productsinorder.order in ( select order_order.order_uuid from order_order where order_order.status = 3);"
	_cursor.execute(_sel)
	records = _cursor.fetchall()
	reporte = []
	for row in records:
		reporte.append({"order":row[0], "product_id": row[1], "product_name": row[2], "product_cant": row[3], "price_unit": row[4], "total in order": row[5]})

	return JsonResponse({'status': True, "provider_sells": reporte}, status=200)