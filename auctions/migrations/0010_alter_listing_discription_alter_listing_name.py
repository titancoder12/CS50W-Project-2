# Generated by Django 4.0.5 on 2022-07-02 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_listing_discription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='discription',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='listing',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
