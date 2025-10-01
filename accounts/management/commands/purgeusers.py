from django.core.management.base import BaseCommand
from database.database import get_engine
from sqlmodel import Session, select
from database.tables import Users

class Command(BaseCommand):
    help = "Delete all users (CAUTION). Optionally filter by domain."

    def add_arguments(self, parser):
        parser.add_argument('--domain', help='Only delete users with this email domain')
        parser.add_argument('--yes-i-am-sure', action='store_true', help='Confirm destructive action')

    def handle(self, *args, **options):
        if not options['yes_i_am_sure']:
            self.stderr.write('Refusing to proceed without --yes-i-am-sure')
            return
        domain = options.get('domain')
        engine = get_engine()
        deleted = 0
        with Session(engine) as session:
            stmt = select(Users)
            users = session.exec(stmt).all()
            for user in users:
                if domain and not user.email.lower().endswith('@'+domain.lower()):
                    continue
                session.delete(user)
                deleted += 1
            session.commit()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} users'))
