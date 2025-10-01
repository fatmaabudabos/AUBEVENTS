import json
import requests
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send a test email using SendGrid REST (if key set) then fallback to Django email; prints diagnostics."

    def add_arguments(self, parser):
        parser.add_argument('--to', required=True, help='Recipient email')
        parser.add_argument('--subject', default='AUBEVENTS Test Email', help='Subject line')
        parser.add_argument('--html', action='store_true', help='Send HTML variant (REST only)')

    def handle(self, *args, **options):
        to_email = options['to']
        subject = options['subject']
        use_html = options['html']

        from_email = getattr(settings, 'VERIFIED_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        api_key = getattr(settings, 'SENDGRID_API_KEY', None)

        self.stdout.write(self.style.NOTICE('=== Email Diagnostics ==='))
        self.stdout.write(f"EMAIL_BACKEND          : {settings.EMAIL_BACKEND}")
        self.stdout.write(f"SENDGRID_API_KEY set   : {bool(api_key)}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL     : {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"VERIFIED_FROM_EMAIL    : {from_email}")
        self.stdout.write(f"SMTP Host/Port         : {getattr(settings,'EMAIL_HOST','')}:{getattr(settings,'EMAIL_PORT','')}")
        self.stdout.write(f"Target Recipient       : {to_email}")
        self.stdout.write('---------------------------')

        # Attempt REST first if API key present
        if api_key:
            self.stdout.write(self.style.NOTICE('Attempting SendGrid REST API send ...'))
            payload = {
                'personalizations': [{ 'to': [{'email': to_email}] }],
                'from': { 'email': from_email },
                'subject': subject,
                'content': []
            }
            if use_html:
                payload['content'].append({'type': 'text/plain', 'value': 'HTML capable client required.'})
                payload['content'].append({'type': 'text/html', 'value': '<strong>AUBEVENTS HTML Test</strong><br/>This confirms SendGrid REST is working.'})
            else:
                payload['content'].append({'type': 'text/plain', 'value': 'If you received this, SendGrid REST is working.'})

            try:
                resp = requests.post(
                    'https://api.sendgrid.com/v3/mail/send',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    data=json.dumps(payload),
                    timeout=10
                )
                if 200 <= resp.status_code < 300:
                    self.stdout.write(self.style.SUCCESS('REST send accepted (2xx). Check your inbox.'))
                    return
                else:
                    self.stderr.write(self.style.ERROR(f'Rest send failed status={resp.status_code} body={resp.text[:500]}'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'Rest send exception: {exc}'))
        else:
            self.stdout.write(self.style.WARNING('No SENDGRID_API_KEY set; skipping REST attempt.'))

        # Fallback to Django send_mail (SMTP or console backend)
        self.stdout.write(self.style.NOTICE('Attempting Django send_mail fallback ...'))
        try:
            sent = send_mail(
                subject=subject,
                message='Fallback plain text body.' ,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False
            )
            if sent:
                self.stdout.write(self.style.SUCCESS('Django backend sent message (fallback).'))
            else:
                self.stderr.write(self.style.ERROR('Django backend returned 0 (not sent).'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Django backend exception: {e}'))
            self.stderr.write(self.style.WARNING('Check that the from email is a verified Single Sender OR domain authenticated.'))
            self.stderr.write(self.style.WARNING('If using a Gmail address, ensure you completed the verification link in SendGrid Single Sender setup.'))
            raise SystemExit(1)
