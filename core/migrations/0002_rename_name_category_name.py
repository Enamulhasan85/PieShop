# Generated by Django 4.1.1 on 2022-10-01 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='Name',
            new_name='name',
        ),
    ]
