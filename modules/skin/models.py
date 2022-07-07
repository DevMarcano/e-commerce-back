from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Skin(models.Model):
	user = models.ForeignKey(User, related_name='user', verbose_name='usuario', db_index=True, on_delete= models.CASCADE)
	nombre_plataforma = models.CharField(max_length=200, verbose_name='Nombre de la plataforma')
	domain = models.CharField(max_length=200, verbose_name='Url de su plataforma')
	logo_plataforma = models.CharField(max_length=200, blank=True, null=True)
	status = models.BooleanField(verbose_name='Activar skin?', default=True)
	prefijo = models.CharField(max_length=5, verbose_name='Prefijo de usuarios')
	banner = models.TextField()
	can_do = models.TextField()
	footer = models.TextField()	
	
	class Meta:
		verbose_name = _('skin')
		verbose_name_plural = _('skins')
		app_label = 'skin'

	def __unicode__(self):
		return "%s" % (self.nombre_plataforma)

# Create your models here.
