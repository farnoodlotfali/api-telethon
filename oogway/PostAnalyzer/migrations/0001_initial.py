# Generated by Django 4.0.5 on 2023-12-08 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='PostInitial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateTimeField()),
                ('channel_id', models.CharField(max_length=50)),
                ('message', models.CharField(max_length=6000)),
                ('message_id', models.CharField(max_length=50)),
                ('reply_to_msg_id', models.CharField(max_length=15)),
                ('edit_date', models.CharField(max_length=100)),
            ],
        ),
    ]
