# Generated by Django 4.0.5 on 2022-06-30 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_listing_discription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='discription',
            field=models.TextField(max_length=100),
        ),
    ]
