# contest/migrations/000X_add_group_matches.py

from django.db import migrations
from datetime import datetime

group_matches = [
    {"group": "A", "home_team": "Germany", "away_team": "Scotland", "date": "2024-06-14 21:00", "place": "Munich"},
    {"group": "A", "home_team": "Scotland", "away_team": "Switzerland", "date": "2024-06-19 21:00", "place": "Cologne"},
    {"group": "B", "home_team": "Spain", "away_team": "Croatia", "date": "2024-06-15 18:00", "place": "Berlin"},
    {"group": "B", "home_team": "Croatia", "away_team": "Italy", "date": "2024-06-24 21:00", "place": "Leipzig"},
    {"group": "C", "home_team": "Denmark", "away_team": "England", "date": "2024-06-20 18:00", "place": "Frankfurt"},
    {"group": "C", "home_team": "Serbia", "away_team": "England", "date": "2024-06-16 21:00", "place": "Gelsenkirchen"},
    {"group": "D", "home_team": "Netherlands", "away_team": "France", "date": "2024-06-21 21:00", "place": "Leipzig"},
    {"group": "D", "home_team": "Austria", "away_team": "France", "date": "2024-06-17 21:00", "place": "Düsseldorf"},
    {"group": "E", "home_team": "Belgium", "away_team": "Slovakia", "date": "2024-06-17 18:00", "place": "Frankfurt"},
    {"group": "E", "home_team": "Romania", "away_team": "Ukraine", "date": "2024-06-17 15:00", "place": "Munich"},
    {"group": "F", "home_team": "Turkey", "away_team": "Portugal", "date": "2024-06-22 18:00", "place": "Dortmund"},
    {"group": "F", "home_team": "Czech Republic", "away_team": "Turkey", "date": "2024-06-26 21:00", "place": "Hamburg"},
    {"group": "A", "home_team": "Poland", "away_team": "Netherlands", "date": "2024-06-16 15:00", "place": "Hamburg"},
    {"group": "A", "home_team": "Poland", "away_team": "Austria", "date": "2024-06-21 18:00", "place": "Berlin"},
    {"group": "A", "home_team": "France", "away_team": "Poland", "date": "2024-06-25 18:00", "place": "Dortmund"}
]

def add_group_matches(apps, schema_editor):
    Match = apps.get_model('contest', 'Match')
    for match in group_matches:
        Match.objects.create(
            group=match['group'],
            home_team=match['home_team'],
            away_team=match['away_team'],
            date=datetime.strptime(match['date'], '%Y-%m-%d %H:%M'),
            place=match['place']
        )

class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0005_create_superuser'),
    ]

    operations = [
        migrations.RunPython(add_group_matches),
    ]
