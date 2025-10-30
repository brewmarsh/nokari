import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create an admin user if one does not exist"

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            username = input("Enter admin username: ")
            email = input("Enter admin email: ")
            password = getpass.getpass("Enter admin password: ")

            User.objects.create_superuser(
                email=email,
                password=password,
                username=username,
                role="admin",
            )
            self.stdout.write(self.style.SUCCESS(
                "Admin user created successfully."))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists."))
