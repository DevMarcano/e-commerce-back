from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from modules.skin.models import Skin

class Category(models.Model):
	Name = models.CharField(max_length=250, blank=True, null=True)
	Description = models.CharField(max_length=250, blank=True, null=True)
	Status = models.BooleanField(default=False, db_index=True)
	
	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categorys')
		app_label = 'products'

	def Serialize(self):
		return {"id": self.pk, "Name": self.Name, "Description": self.Description, "Status": self.Status }

class Provider(models.Model):
	Name = models.CharField(max_length=250, blank=True, null=True)
	Priority = models.IntegerField(blank=True, null=True)
	Phone = models.CharField(max_length=250, blank=True, null=True)
	Description = models.CharField(max_length=250, blank=True, null=True)
	Email = models.CharField(max_length=250, blank=True, null=True)
	Url = models.CharField(max_length=250, blank=True, null=True)
	Status = models.BooleanField(default=False, db_index=True)
	
	def Serialize(self):
		return {"id": self.pk, "Name": self.Name, "Priority": self.Priority, "Phone": self.Phone , "Url": self.Url ,"Email": self.Email, "Description": self.Description, "Status": self.Status }

class Product(models.Model):
	Name = models.CharField(max_length=250, blank=True, null=True)
	Marca = models.CharField(max_length=250, blank=True, null=True)
	Model = models.CharField(max_length=250, blank=True, null=True)
	Category = models.OneToOneField(Category, related_name="Category", db_index=True, on_delete= models.CASCADE)
	Prov = models.OneToOneField(Provider, related_name="Provider", db_index=True, on_delete= models.CASCADE) 
	User = models.OneToOneField(User, related_name="User", db_index=True, on_delete= models.CASCADE)
	Status = models.BooleanField(default=False, db_index=True)
	Precio = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	Skin = models.IntegerField(blank=True, null=True)
	Cantidad = models.IntegerField(blank=True, null=True)
	SerialCode = models.CharField(max_length=250, blank=True, null=True)
	Description = models.CharField(max_length=250, blank=True, null=True)
	
	class Meta:
		verbose_name = _('product')
		verbose_name_plural = _('products')
		app_label = 'products'

	def Serialize(self):
		return {"id": self.pk, "Name": self.Name, "Marca": self.Marca, "Model": self.Model, "Category": self.Category.Name ,"Provider": self.Prov.Name, "User": self.User.username, "Precio": float(self.Precio), "Cantidad": int(self.Cantidad), "SerialCode": self.SerialCode, "Description": self.Description, "Status": self.Status }

# Create your models here.
