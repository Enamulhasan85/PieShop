# Generated by Django 4.1.1 on 2023-01-13 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_product_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='productcode',
            field=models.CharField(default='BST-498', max_length=100),
            preserve_default=False,
        ),
    ]