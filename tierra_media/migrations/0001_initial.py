# Generated by Django 4.2.18 on 2025-02-27 07:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Armor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('icon', models.ImageField(blank=True, upload_to='uploads/')),
                ('defense', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Backpack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo electrónico')),
                ('subject', models.CharField(max_length=200, verbose_name='Asunto')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
            ],
            options={
                'verbose_name': 'Mensaje de contacto',
                'verbose_name_plural': 'Mensajes de contacto',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('La Comunidad del Anillo', 'La Comunidad del Anillo'), ('Lothlorien', 'Lothlorien'), ('Rivendel', 'Rivendel'), ('Mordor', 'Mordor'), ('Isengard', 'Isengard')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Minas Tirith', 'Minas Tirith'), ('Bosque Negro', 'Bosque Negro'), ('Lothlorien', 'Lothlorien'), ('Hobbiton', 'Hobbiton'), ('Rivendel', 'Rivendel'), ('Isengard', 'Isengard'), ('Mordor', 'Mordor')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Humano', 'Humano'), ('Elfo', 'Elfo'), ('Enano', 'Enano'), ('Hobbit', 'Hobbit'), ('Orco', 'Orco')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('icon', models.ImageField(blank=True, upload_to='uploads/')),
                ('damage', models.IntegerField()),
                ('type', models.CharField(max_length=50)),
                ('backpack', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tierra_media.backpack')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.ImageField(blank=True, upload_to='uploads/')),
                ('name', models.CharField(max_length=50)),
                ('sex', models.CharField(choices=[('M', 'Hombre'), ('F', 'Mujer')], max_length=1)),
                ('max_health', models.IntegerField(default=250)),
                ('health', models.IntegerField(default=250)),
                ('defense', models.IntegerField(default=50)),
                ('npc', models.BooleanField(default=False)),
                ('equipped_armor', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tierra_media.armor')),
                ('equipped_weapon', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tierra_media.weapon')),
                ('faction', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='tierra_media.faction')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='tierra_media.location')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='tierra_media.race')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='backpack',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tierra_media.character'),
        ),
        migrations.AddField(
            model_name='armor',
            name='backpack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tierra_media.backpack'),
        ),
        migrations.AddField(
            model_name='armor',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
