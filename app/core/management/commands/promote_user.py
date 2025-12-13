from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import firestore
# Import to ensure Firebase Admin SDK is initialized
from app.core import authentication  # noqa: F401

User = get_user_model()

class Command(BaseCommand):
    help = 'Promote a user to admin in Django and Firestore'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to promote')

    def handle(self, *args, **options):
        email = options['email']

        # 1. Promote in Django
        try:
            user = User.objects.get(email=email)
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {email} promoted in Django."))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"User {email} not found in Django DB. Attempting to create..."))
            try:
                user = User.objects.create_superuser(email=email, username=email, password=None) # Password not set, auth via Firebase
                user.role = 'admin'
                user.save()
                self.stdout.write(self.style.SUCCESS(f"User {email} created and promoted in Django."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create user in Django: {e}"))

        # 2. Promote in Firestore
        try:
            # Check if Firebase App is initialized
            try:
                firebase_admin.get_app()
            except ValueError:
                self.stdout.write(self.style.ERROR("Firebase Admin SDK not initialized."))
                return

            db = firestore.client()
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = list(query.stream())

            if docs:
                for doc in docs:
                    doc.reference.update({'role': 'admin'})
                    self.stdout.write(self.style.SUCCESS(f"User {email} (uid: {doc.id}) promoted in Firestore."))
            else:
                 self.stdout.write(self.style.WARNING(f"User {email} not found in Firestore. Make sure they have logged in at least once."))

        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Error updating Firestore: {e}"))
