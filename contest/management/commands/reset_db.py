# contest/management/commands/clear_db.py

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Clears all data from all user-defined database tables'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write('This command can only be run in DEBUG mode.')
            return

        self.stdout.write('Disabling foreign key checks...')

        # Disable foreign key checks
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF;")
        self.stdout.write('Foreign key checks disabled.')

        self.stdout.write('Clearing all user-defined tables...')

        # Get all user-defined tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # List of system tables to skip
        system_tables = ['sqlite_sequence', 'django_migrations']

        # Clear all user-defined tables
        for table in tables:
            if table[0] not in system_tables:
                self.stdout.write(f'Clearing table {table[0]}')
                cursor.execute(f'DELETE FROM {table[0]}')
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table[0]}'")

        self.stdout.write('All user-defined tables cleared.')

        self.stdout.write('Enabling foreign key checks...')
        cursor.execute("PRAGMA foreign_keys=ON;")
        self.stdout.write('Foreign key checks enabled.')

        self.stdout.write('Database cleared successfully.')
