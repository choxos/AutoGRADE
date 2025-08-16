"""
Management command to create the default superuser for AutoGRADE.

This command creates a default superuser with predefined credentials.
WARNING: This is intended for development/demo purposes only.
For production environments, create superusers manually with secure credentials.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Creates the default superuser for AutoGRADE development/demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user already exists (will update password)',
        )

    def handle(self, *args, **options):
        username = 'choxos'
        email = 'ahmad.pub@gmail.com'
        password = '!*)@&)'
        
        try:
            if User.objects.filter(username=username).exists():
                if options['force']:
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.email = email
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully updated superuser "{username}"')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Superuser "{username}" already exists. Use --force to update.')
                    )
                    return
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}"')
                )
                
            self.stdout.write('Default superuser credentials:')
            self.stdout.write(f'  Username: {username}')
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Password: {password}')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: These are default development credentials. '
                    'Change them immediately in production environments!'
                )
            )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
