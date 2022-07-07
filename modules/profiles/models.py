# -*- coding: UTF-8 -*
from __future__ import unicode_literals
from pyexpat import model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	user = models.OneToOneField(User, related_name="usuario", db_index=True, on_delete= models.CASCADE)
	status = models.BooleanField(default=False, db_index=True)
	balance = models.DecimalField(max_digits=16, decimal_places=6, blank=False, null=False)
	last_touch = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	skin_id = models.IntegerField(blank=True, null=True)
	direction = models.CharField(max_length=250, blank=True, null=True)
	phone = models.CharField(max_length=50, blank=True, null=True)
	#last_ip = models.IntegerField()
	#last_ips = models.CharField(max_length=120, blank=True, null=True)

	class Meta:
		verbose_name = _('Perfil')
		verbose_name_plural = _('Perfiles')
		app_label = 'Profiles'

	def __unicode__(self):
		return "%s - %s - %s" % (self.user, self.balance, self.status)

class SessionToken(models.Model):
	user = models.OneToOneField(User, related_name="Session_User_Token",on_delete= models.CASCADE)
	token = models.CharField(max_length=120, blank=False, null=False)
	created_date = models.DateTimeField(db_index=True)
	expire_hour = models.IntegerField(blank=False, null=False, default=7200)
	domain = models.CharField(max_length=30, blank=True, null=True)
	#user_ip = models.CharField(max_length=30, blank=False, null=False)

	class Meta:
		verbose_name = _('Session Token')
		verbose_name_plural = _('Session Tokens')
		app_label = 'profiles'

	def __unicode__(self):
		return "%s - %s"%(self.user.username, self.token)


class UserToken(models.Model):
	user = models.OneToOneField(User, related_name="User_Token",on_delete= models.CASCADE)
	token = models.CharField(max_length=120, blank=False, null=False)

	class Meta:
		verbose_name = _('User Token')
		verbose_name_plural = _('Users Tokens')
		app_label = 'profiles'

	def __unicode__(self):
		return "%s - %s"%(self.user.username, self.token)

# Create your models here.
