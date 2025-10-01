import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "List SendGrid verified single senders and domain authenticated identities (REST)."

    def handle(self, *args, **options):
        api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not api_key:
            self.stderr.write('SENDGRID_API_KEY not set in environment.')
            return
        headers = { 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json' }

        # Single Senders
        try:
            r = requests.get('https://api.sendgrid.com/v3/verified_senders', headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                self.stdout.write(self.style.NOTICE('Single Senders:'))
                for sender in data.get('results', []):
                    self.stdout.write(f" - {sender.get('from_email')} (verified={sender.get('verified')})")
            else:
                self.stderr.write(f'Failed to fetch single senders: {r.status_code} {r.text[:200]}')
        except Exception as e:
            self.stderr.write(f'Error fetching single senders: {e}')

        # Authenticated Domains
        try:
            r = requests.get('https://api.sendgrid.com/v3/whitelabel/domains', headers=headers, timeout=10)
            if r.status_code == 200:
                domains = r.json()
                self.stdout.write(self.style.NOTICE('Authenticated Domains:'))
                for dom in domains:
                    self.stdout.write(f" - {dom.get('domain')} (valid={dom.get('valid')})")
            else:
                self.stderr.write(f'Failed to fetch domains: {r.status_code} {r.text[:200]}')
        except Exception as e:
            self.stderr.write(f'Error fetching domains: {e}')

        self.stdout.write(self.style.SUCCESS('Done.'))
