# Generated by Django 4.0.3 on 2022-07-20 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_provider_rename_cantidad_product_cantidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='Description',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='Model',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
