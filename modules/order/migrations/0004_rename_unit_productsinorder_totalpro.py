# Generated by Django 4.0.3 on 2022-07-22 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_productsinorder_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productsinorder',
            old_name='unit',
            new_name='totalPro',
        ),
    ]
