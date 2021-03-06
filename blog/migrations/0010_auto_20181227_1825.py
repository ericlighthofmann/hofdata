# Generated by Django 2.1.3 on 2018-12-28 02:25

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20181227_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.core.fields.StreamField([('code', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.TextBlock()), ('paragraph', wagtail.core.blocks.TextBlock()), ('code', wagtail.core.blocks.StructBlock([('language', wagtail.core.blocks.ChoiceBlock(choices=[('python', 'Python')], help_text='Coding language', label='Language')), ('code', wagtail.core.blocks.TextBlock(label='Code'))], label='Python', language='python'))]))]),
        ),
    ]
