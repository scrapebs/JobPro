# Generated by Django 2.0 on 2018-03-03 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobpro', '0012_auto_20180303_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cv',
            name='created_date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='cv',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orginfo',
            name='organisation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='created_date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancies', to=settings.AUTH_USER_MODEL),
        ),
    ]
