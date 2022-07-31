# Generated by Django 4.0.3 on 2022-07-22 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_uuid', models.CharField(blank=True, max_length=250, null=True)),
                ('user', models.IntegerField(db_index=True)),
                ('status', models.IntegerField(default=3)),
                ('total', models.DecimalField(decimal_places=6, max_digits=16)),
                ('skin_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
