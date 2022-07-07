from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from modules.skin.models import Skin

class category(models.Model):
	Name = models.CharField(max_length=250, blank=True, null=True)
	Description = models.CharField(max_length=250, blank=True, null=True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categorys')
		app_label = 'products'

class Provider(models.Model):

	class Meta:
		verbose_name = _('provider')
		verbose_name_plural = _('providers')
		app_label = 'provider'


class Product(models.Model):
	Name = models.CharField(max_length=250, blank=True, null=True)
	marca = models.CharField(max_length=250, blank=True, null=True)
	category = models.OneToOneField(category, related_name="Categorys", db_index=True, on_delete= models.CASCADE)
	prov = models.CharField(max_length=250, blank=True, null=True) # colocar proveedores luego 
	userpost = models.OneToOneField(User, related_name="usuario", db_index=True, on_delete= models.CASCADE)
	status = models.BooleanField(default=False, db_index=True)
	precio = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	skin_id = models.IntegerField(blank=True, null=True)
	cantidad = models.IntegerField(blank=True, null=True)
	serialCode = models.CharField(max_length=250, blank=True, null=True)

	class Meta:
		verbose_name = _('product')
		verbose_name_plural = _('products')
		app_label = 'products'

	def __unicode__(self):
		return "%s - %s - %s" % (self.user, self.balance, self.status)



# Create your models here.
