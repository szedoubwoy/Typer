# contest/migrations/000X_load_teams.py
from django.db import migrations
import json
import os


def load_teams(apps, schema_editor):
    Team = apps.get_model('contest', 'Team')

    with open('scripts/teams.json', encoding='utf-8') as f:
        teams = json.load(f)

    # Załaduj drużyny do bazy danych
    for team_data in teams:
        Team.objects.update_or_create(name=team_data['team'])


class Migration(migrations.Migration):
    dependencies = [
        ('contest', '0013_team_tournamentwinnerselection'),
    ]

    operations = [
        migrations.RunPython(load_teams),
    ]
