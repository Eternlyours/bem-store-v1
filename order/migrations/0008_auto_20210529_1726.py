# Generated by Django 3.1.7 on 2021-05-29 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20210525_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='key',
            field=models.CharField(default='c89c104a-b', max_length=10, unique=True, verbose_name='Код заказа'),
        ),
    ]