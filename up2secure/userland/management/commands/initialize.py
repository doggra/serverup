from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from userland.models import Profile

class Command(BaseCommand):

    def handle(self, *args, **options):

        user = User(username="Administrator", account_type=2, is_staff=True, is_superuser=True)
        user.set_password('admin2017')
        user.save()
        profile = Profile(user=user, account_type=2)
        profile.save()
        print("User {0} crated".format(user.username))

        user = User(username="Customer")
        user.set_password('custom2017')
        user.save()
        profile = Profile(user=user, account_type=0)
        profile.save()
        print("User {0} crated".format(user.username))