# Generated by Django 2.1.3 on 2019-01-06 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocktrendsbot', '0006_auto_20190106_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='postrepliedto',
            name='url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]
