# Generated by Django 2.1.3 on 2019-01-17 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocktrendsbot', '0007_postrepliedto_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsRunning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_running', models.BooleanField(default=False)),
            ],
        ),
    ]