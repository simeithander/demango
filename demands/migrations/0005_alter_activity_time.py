# Generated by Django 5.1.1 on 2024-10-09 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demands', '0004_alter_demands_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='time',
            field=models.CharField(max_length=20),
        ),
    ]