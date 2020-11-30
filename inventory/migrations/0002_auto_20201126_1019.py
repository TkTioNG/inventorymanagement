# Generated by Django 3.1.3 on 2020-11-26 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='materialstock',
            constraint=models.UniqueConstraint(fields=('store', 'material'), name='unique_store_material'),
        ),
    ]