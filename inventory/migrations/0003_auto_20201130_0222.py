# Generated by Django 3.1.3 on 2020-11-30 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20201126_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='stores', to='inventory.Product'),
        ),
    ]
