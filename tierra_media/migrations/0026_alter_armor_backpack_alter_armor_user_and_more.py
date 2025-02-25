# Generated by Django 4.2.18 on 2025-02-25 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tierra_media', '0025_alter_character_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='armor',
            name='backpack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tierra_media.backpack'),
        ),
        migrations.AlterField(
            model_name='armor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='backpack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tierra_media.backpack'),
        ),
    ]
