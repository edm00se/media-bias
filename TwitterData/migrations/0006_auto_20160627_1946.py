# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TwitterData', '0005_auto_20160315_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='senator',
            field=models.ForeignKey(related_query_name='search', related_name='searches', to='TwitterData.Senator'),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='search',
            field=models.ForeignKey(related_query_name='tweet', related_name='tweets', to='TwitterData.Search'),
        ),
    ]
