from django.core.management.base import BaseCommand
from sqlalchemy import text
from database.database import get_engine

class Command(BaseCommand):
    help = 'List events and their created_by values'

    def handle(self, *args, **options):
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT id, title, created_by FROM events ORDER BY id DESC LIMIT 50
            """))
            rows = result.fetchall()
            if not rows:
                self.stdout.write("No events found.")
                return
            for r in rows:
                self.stdout.write(f"#{r[0]}: {r[1]} -> created_by={r[2]}")
