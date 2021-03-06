# Generated by Django 4.0.3 on 2022-04-19 20:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Skin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_plataforma', models.CharField(max_length=200, verbose_name='Nombre de la plataforma')),
                ('domain', models.CharField(max_length=200, verbose_name='Url de su plataforma')),
                ('logo_plataforma', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.BooleanField(default=True, verbose_name='Activar skin?')),
                ('prefijo', models.CharField(max_length=5, verbose_name='Prefijo de usuarios')),
                ('banner', models.TextField()),
                ('can_do', models.TextField()),
                ('footer', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'skin',
                'verbose_name_plural': 'skins',
            },
        ),
    ]
