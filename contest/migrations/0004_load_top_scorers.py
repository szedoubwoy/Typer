# contest/migrations/000X_load_top_scorers.py
from django.db import migrations
import json
import os

def load_top_scorers(apps, schema_editor):
    TopScorer = apps.get_model('contest', 'TopScorer')

    with open('scripts/top_scorers_cleaned.json', encoding='utf-8') as f:
        players = json.load(f)

    # Wstawienie zawodników do modelu TopScorer
    for name, country in players:
        TopScorer.objects.update_or_create(
            player_name=name,
            defaults={'country': country}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_load_teams'),  # Zaktualizuj według swojej numeracji migracji
    ]

    operations = [
        migrations.RunPython(load_top_scorers),
    ]
