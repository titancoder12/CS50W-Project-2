# Generated by Django 4.0.5 on 2022-07-02 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_listing_discription_alter_listing_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='price',
            new_name='amount',
        ),
    ]
