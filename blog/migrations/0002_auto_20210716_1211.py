# Generated by Django 3.1.7 on 2021-07-16 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'Блог компании', 'verbose_name_plural': 'Блог компании'},
        ),
    ]
