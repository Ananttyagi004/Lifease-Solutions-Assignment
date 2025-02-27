# Generated by Django 5.1.2 on 2024-10-30 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_id', models.CharField(max_length=20, unique=True)),
                ('team_a', models.CharField(max_length=50)),
                ('team_b', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField()),
                ('team_a_squad', models.JSONField(default=list)),
                ('team_b_squad', models.JSONField(default=list)),
                ('live_data', models.JSONField(default=dict)),
                ('scorecard_data', models.JSONField(default=dict)),
            ],
        ),
    ]
