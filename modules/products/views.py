from pyexpat import model
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from modules.skin.models import Skin
from modules.core.login_decorateds import AuthToken, GetMethod, NewApiToken, CBMethod, ADLock, PostMethod
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from modules.products.models import Product, Provider, Category
from modules.core.extras import ValidatedPass, get_profile_by_user, close, new_token, gen_token, check_date, all_countries, GetCountry, clean_domain, ValidatedEmail, ValidatedUsername, refresh_token, percent_rollover
from modules.core.tasks import _send_email, UpdateProfile, _new_user_token
from django.contrib.auth import login, authenticate, logout
import json

@PostMethod
@csrf_exempt
def register_Product(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)

	try:
		Name = json_data['name']
		Marca = json_data['marca']
		_Model = json_data['model']
		category = json_data['category']
		Prov = json_data['provider']
		UserPost =json_data['user']
		Precio = json_data['price']
		# Skin_id = json_data['Skin_id']
		Cant = json_data['cant']
		SerialCode = json_data['serialCode']
		description = json_data['description']
		# _domain = json_data['domain']
		# _country_id = int(json_data['country'])
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)

	_clean_url = "localhost:8000"#clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	
	_prov = Provider.objects.filter(id=Prov)
	if not _prov.exists():
		return JsonResponse({'status': False, 'message': 'Provider Not Found'}, status=403)
	_prov = _prov[0]
	
	_user = User.objects.filter(id=UserPost)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	category = Category.objects.filter(Name=category)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	category = category[0]

	_product = Product.objects.filter(Name=Name, Prov=Prov, Skin=1) 
	if _product.exists():
		return JsonResponse({'status':False, 'message':'Product already'}, status=403)

	try:
		_newproduct = Product.objects.create(Name=Name, Marca=Marca, Model=_Model, Description=description, Category=category, Prov=_prov, User=_user[0], Precio=Precio, Skin=platfs[0].id, Cantidad=Cant, SerialCode=SerialCode, Status=True)
		_newproduct.save()
	except:
		return JsonResponse({'status':False, 'message':'error creating product'}, status=403)

	return JsonResponse({'status':True, "Product": _newproduct.Serialize()}, status=200)


@PostMethod
@csrf_exempt
def update_Product(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)

	try:
		ProdId = json_data['id']
		Name = json_data['name']
		Marca = json_data['marca']
		Model = json_data['model']
		_Category = json_data['category']
		_Prov = json_data['prov']
		UserPost =json_data['user']
		Precio = json_data['price']
		# Skin_id = json_data['Skin_id']
		Cant = json_data['cant']
		SerialCode = json_data['serialCode']
		Status = json_data['status']
		# _domain = json_data['domain']
		# _country_id = int(json_data['country'])
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)

	_clean_url = clean_domain(request.get_host())

	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	if not platfs.exists():
		return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	
	_prov = Provider.objects.filter(id=_Prov)
	if not _prov.exists():
		return JsonResponse({'status': False, 'message': 'Provider Not Found'}, status=403)

	_user = User.objects.filter(id=UserPost)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	category = Category.objects.filter(Name=_Category)
	if not _user.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	category = category[0]

	_prod = Product.objects.filter(id=ProdId, Prov=_prov[0].id)
	if not _prod.exists():
		return JsonResponse({'status': False, 'message': 'Error product Not Found for this provider'}, status=403)
	_prod=_prod[0]

	try:
		_prod.Name = Name
		_prod.marca = Marca
		_prod.Model = Model
		_prod.Category = category
		# _prod.Prov = Prov
		_prod.Userpost = UserPost
		_prod.Precio = Precio
		# _prod.Skin_id = Skin_id
		_prod.Cantidad = int(Cant)
		_prod.SerialCode = SerialCode
		_prod.Status = Status
		_prod.save()
	except:
		return JsonResponse({'status': False, 'message': 'Error Updating Product'}, status=403)

	return JsonResponse({'status': True, "Product": _prod.Serialize()}, status=200)

"""
@csrf_exempt
@PostMethod
def change_Product_state(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)
	try:
		Id = json_data['Id']
		Status = json_data['Status']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	
	_product = Product.objects.filter(id=Id, skin=platfs.id)

	if not _product.exists():
		return JsonResponse({'status':False, 'message':'Product Not Exist'}, status=403)
	_product = _product[0]

	try:
		_product.Status = Status
	except:
		return JsonResponse({'status':False, 'message':'Update State Faild'}, status=403)

	return JsonResponse({'status': True, 'Product': _product[0].Serialize()}, status=200)"""


@csrf_exempt
@PostMethod
def get_Product(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status': False, 'message': 'Json Incorrecto'}, status=403)
	try:
		Id = json_data['id']
	except:
		return JsonResponse({'status': False, 'message': 'Parametros Incorrectos'}, status=403)
	
	_clean_url = "localhost:8000" # clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	
	_product = Product.objects.filter(id=Id, Skin=platfs[0].id)

	if not _product.exists():
		return JsonResponse({'status': False, 'message': 'Product Not Exist'}, status=403)
	
	_product= _product[0]

	return JsonResponse({'status': True, 'Product': _product.Serialize()}, status=200)


@csrf_exempt
@PostMethod
def get_Products(request):
	print(clean_domain(request.get_host()))
	_clean_url = "localhost:8000" # clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	_products = Product.objects.filter(Skin=platfs[0].id)
	
	if not _products.exists():
		return JsonResponse({'status': False, 'message': 'Not list Product'}, status=403)
	
	listP = []
	for dat in _products:
		listP.append(dat.Serialize())
	print(listP)
	return JsonResponse({"status": True, "Products": listP}, status=200)


@csrf_exempt
@PostMethod
def get_Products_by_category(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)
	try:
		category = json_data['category']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	
	_category = Category.objects.filter(Name=category)
	if not _category.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	_category = _category[0].id
	
	_products = Product.objects.filter(Skin=platfs[0].id, Category=_category)

	if not _products.exists():
		return JsonResponse({'status': False, 'message': 'Not list Product'}, status=403)
	
	listP = []
	for dat in _products:
		listP.append(dat.Serialize())

	return JsonResponse({'status': True, 'Products': listP}, status=200)


@csrf_exempt
@PostMethod
def get_Products_by_Provider(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)
	try:
		provider = json_data['provider']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	
	_Provider = Provider.objects.filter(Name=provider)
	if not _Provider.exists():
		return JsonResponse({'status': False, 'message': 'Error User Not Found'}, status=403)

	_Provider = _Provider[0].id
	
	_products = Product.objects.filter(Skin=platfs[0].id, Prov=_Provider)
		
	if not _products.exists():
		return JsonResponse({'status': False, 'message': 'Not list Product'}, status=403)
	
	listP = []
	for dat in _products:
		listP.append(dat.Serialize())

	return JsonResponse({'status': True, 'Products': listP}, status=200)


@csrf_exempt
@PostMethod
def get_Products_by_Search_Name(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message': 'Json Incorrecto'}, status=403)
	try:
		name = json_data['name']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = "localhost:8000" #clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar

	_products = Product.objects.filter(Skin=platfs[0].id, Name__contains=name)
	
	if not _products.exists():
		return JsonResponse({'status': False, 'message': 'Not list Product'}, status=403)
	
	listP = []
	for dat in _products:
		listP.append(dat.Serialize())

	return JsonResponse({'status': True, 'Products': listP}, status=200)


@csrf_exempt
@PostMethod
def create_Category(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message': 'Json Incorrecto'}, status=403)
	try:
		_name = json_data['name']
		_description = json_data['description']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	
	_category = Category.objects.filter(Name=_name)

	if not _category.exists():
		_newcategory = Category.objects.create(Name=_name, Description=_description, Status=True)
		_newcategory.save()
	else:
		return JsonResponse({'status': False, 'message': 'Category already'}, status=403)
	
	return JsonResponse({'status': True, 'Products': _newcategory.Serialize()}, status=200)


@csrf_exempt
@PostMethod
def update_Category(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message': 'Json Incorrecto'}, status=403)
	try:
		_name = json_data['name']
		_Description = json_data['description']
		_Status = json_data['status']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	# _clean_url = clean_domain(request.get_host())
	# platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar

	_category = Category.objects.filter(Name=_name)

	if not _category.exists():
		return JsonResponse({'status':False, 'message':'Category not exist'}, status=403)
	_category = _category[0]

	_category.Name = _name
	_category.Description = _Description
	_category.Status = _Status

	return JsonResponse({'status': True, 'Products': _category.Serialize()}, status=200)


@csrf_exempt
@PostMethod
def get_categorys(request):
	# _clean_url = clean_domain(request.get_host())
	# platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	_category = Category.objects.all()
	listCat = []
	for cat in _category:
		listCat.append(cat.Serialize())
	
	return JsonResponse({'status': True, 'Categorys': listCat }, status=200)


@csrf_exempt
@PostMethod
def get_providers(request):
	_prov = Provider.objects.all()
	listCat = []
	for dat in _prov:
		listCat.append(dat.Serialize())
	return JsonResponse({'status': True, 'Providers': listCat }, status=200)


@csrf_exempt
@PostMethod
def create_Provider(request):
	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message': 'Json Incorrecto'}, status=403)
	try:
		_name = json_data['name']
		_description = json_data['description']
		_priority = json_data['priority']
		_phone = json_data['phone']
		_email = json_data['email']
		_url = json_data['url']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)
	
	_clean_url = clean_domain(request.get_host())
	platfs = Skin.objects.filter(domain=_clean_url,status=True)#cambiar
	
	_Provider = Provider.objects.filter(Name=_name)

	if not _Provider.exists():
		_newProvider = Provider.objects.create(Name=_name, Priority=_priority, Phone=_phone, Email=_email, Url=_url, Description=_description, Status=True)
		_newProvider.save()
	else:
		return JsonResponse({'status': False, 'message': 'Provider already'}, status=403)
	
	return JsonResponse({'status': True, 'Products': _newProvider.Serialize()}, status=200)


@PostMethod
@csrf_exempt
def update_Provider(request):

	try:
		json_data = json.loads(request.body)
	except:
		return JsonResponse({'status':False, 'message':'Json Incorrecto'}, status=403)

	try:
		_ProvId = json_data['id']
		_Name = json_data['name']
		_Phone = json_data['phone']
		_priority = json_data['priority']
		_Description = json_data['description']
		_Email =json_data['email']
		_Url = json_data['url']
		_Status = json_data['status']
	except:
		return JsonResponse({'status':False, 'message':'Parametros Incorrectos'}, status=403)

	_clean_url = clean_domain(request.get_host())

	# platfs = Skin.objects.filter(domain=_clean_url, status=True)#cambiar
	# if not platfs.exists():
	# return JsonResponse({'status': False, 'message': 'No se encuentra la skin'}, status=403)
	
	_prov = Provider.objects.filter(id=_ProvId)
	if not _prov.exists():
		return JsonResponse({'status': False, 'message': 'Provider Not Found'}, status=403)
	_prov = _prov[0]

	try:
		_prov.Name = _Name
		_prov.Priority = _priority
		_prov.Phone = _Phone
		_prov.Description = _Description
		_prov.Email = _Email
		_prov.Url = _Url
		_prov.Status = _Status
		_prov.save()
	except:
		return JsonResponse({'status': False, 'message': 'Error Updating Product'}, status=403)

	return JsonResponse({'status': True, "Product": _prov.Serialize()}, status=200)
