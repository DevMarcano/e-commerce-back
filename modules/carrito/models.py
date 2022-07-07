from itertools import product
from django.db import models
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from modules.skin.models import Skin
from modules.products.models import Product


	
class Carrito(models.Model): #factura basicamente 
	orden = models.OneToOneField(Product, related_name="Categorys", db_index=True, on_delete= models.CASCADE)
	user = models.OneToOneField(User, related_name="Usuario", db_index=True, on_delete= models.CASCADE)
	status = models.IntegerField(default=3)# 1:pagado 2:rechazado 3:espera
	total = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	skin_id = models.IntegerField(blank=True, null=True)

	class Meta:
		verbose_name = _('Carrito')
		verbose_name_plural = _('Carritos')
		app_label = 'Carrito'

class ProductsInCarrito(models.Model): #orden basicamente
	car= models.OneToOneField(Carrito, related_name="car", db_index=True, on_delete= models.CASCADE)
	products = models.OneToOneField(Product, related_name="Products", db_index=True, on_delete= models.CASCADE)
	cant = models.IntegerField(blank=True, null=True)
	class Meta:
		verbose_name = _('CarritoXProduct')
		verbose_name_plural = _('CarritoXProductss')
		app_label = 'CarritoXProduct'