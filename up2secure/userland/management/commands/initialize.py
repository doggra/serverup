from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from userland.models import Profile

class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User(username="Administrator", is_staff=True, is_superuser=True)
        user.set_password('admin2017')
        user.save()
        profile = Profile(user=user)
        profile.save()
        print("User {0} crated".format(user.username))