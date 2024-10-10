# Generated by Django 5.1.1 on 2024-10-10 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demands', '0005_alter_activity_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='demands',
            name='demand_type',
            field=models.CharField(choices=[('Projetos / Melhoria', 'Projetos / Melhoria'), ('QAS', 'QAS'), ('Outro', 'Outro')], default='Outro', max_length=20),
        ),
    ]
