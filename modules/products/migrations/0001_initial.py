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
            name='category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(blank=True, max_length=250, null=True)),
                ('Description', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categorys',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(blank=True, max_length=250, null=True)),
                ('marca', models.CharField(blank=True, max_length=250, null=True)),
                ('status', models.BooleanField(db_index=True, default=False)),
                ('precio', models.DecimalField(decimal_places=6, max_digits=16)),
                ('skin_id', models.IntegerField(blank=True, null=True)),
                ('cantidad', models.IntegerField(blank=True, null=True)),
                ('serialCode', models.CharField(blank=True, max_length=250, null=True)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Categorys', to='products.category')),
                ('userpost', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='usuario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
    ]
