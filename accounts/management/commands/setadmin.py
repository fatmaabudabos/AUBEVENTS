from django.core.management.base import BaseCommand, CommandError
from database.database import update_is_admin, get_is_admin


class Command(BaseCommand):
    help = "Set a user's is_admin flag to True"

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to promote to admin')

    def handle(self, *args, **options):
        email = options['email']
        update_is_admin(email, True)
        status = get_is_admin(email)
        if status:
            self.stdout.write(self.style.SUCCESS(f"{email} is now admin"))
        else:
            raise CommandError(f"Failed to set admin for {email}. Ensure the user exists.")
