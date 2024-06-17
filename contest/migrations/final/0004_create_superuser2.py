# migrations/xxxx_create_superuser.py
from django.db import migrations
from django.conf import settings
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='jFW#@a-<kbe*H(~m!6gEQ['
        )

class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_team_is_winner_topscorerselection_confirmed_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]