# Generated by Django 2.2.16 on 2022-08-16 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220816_1952'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='follow_only_once',
        ),
    ]
