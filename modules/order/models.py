from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from modules.skin.models import Skin
from modules.products.models import Product

	
class Order(models.Model): #factura basicamente 
	order_uuid = models.CharField(max_length=250, blank=True, null=True)
	user = models.IntegerField(blank=False, null=False, db_index=True)
	status = models.IntegerField(default=3)# 1:pagado 2:rechazado 3:espera
	total = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	skin_id = models.IntegerField(blank=True, null=True)
	
	def Serialize(self):
		return {"id": self.pk, "orden": self.order_uuid, "user": self.user, "status": self.status , "total": float(self.total)}


class ProductsInOrder(models.Model): #orden basicamente
	order = models.CharField(max_length=250, blank=True, null=True)
	products = models.IntegerField(blank=False, null=False, db_index=True)
	totalPro = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	cant = models.IntegerField(blank=True, null=True)

	def Serialize(self):
		return {"order": self.order, "product": self.products, "unit": float(self.unit), "cant": int(self.cant)}
