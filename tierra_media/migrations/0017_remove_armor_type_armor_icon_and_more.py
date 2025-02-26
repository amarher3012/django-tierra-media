# Generated by Django 4.2.19 on 2025-02-26 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tierra_media', '0016_merge_20250226_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='armor',
            name='type',
        ),
        migrations.AddField(
            model_name='armor',
            name='icon',
            field=models.ImageField(blank=True, upload_to='uploads/'),
        ),
        migrations.AddField(
            model_name='character',
            name='equipped_armor',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tierra_media.armor'),
        ),
        migrations.AddField(
            model_name='character',
            name='equipped_weapon',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tierra_media.weapon'),
        ),
        migrations.AddField(
            model_name='character',
            name='icon',
            field=models.ImageField(blank=True, upload_to='uploads/'),
        ),
        migrations.AddField(
            model_name='character',
            name='sex',
            field=models.CharField(choices=[('M', 'Hombre'), ('F', 'Mujer')], default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='weapon',
            name='icon',
            field=models.ImageField(blank=True, upload_to='uploads/'),
        ),
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
            model_name='faction',
            name='name',
            field=models.CharField(choices=[('La Comunidad del Anillo', 'La Comunidad del Anillo'), ('Lothlorien', 'Lothlorien'), ('Rivendel', 'Rivendel'), ('Mordor', 'Mordor'), ('Isengard', 'Isengard')], max_length=50),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(choices=[('Minas Tirith', 'Minas Tirith'), ('Bosque Negro', 'Bosque Negro'), ('Lothlorien', 'Lothlorien'), ('Hobbiton', 'Hobbiton'), ('Rivendel', 'Rivendel'), ('Isengard', 'Isengard'), ('Mordor', 'Mordor')], max_length=50),
        ),
        migrations.AlterField(
            model_name='race',
            name='name',
            field=models.CharField(choices=[('Humano', 'Humano'), ('Elfo', 'Elfo'), ('Enano', 'Enano'), ('Hobbit', 'Hobbit'), ('Orco', 'Orco')], max_length=50),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='backpack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tierra_media.backpack'),
        ),
        migrations.DeleteModel(
            name='Relationship',
        ),
    ]
