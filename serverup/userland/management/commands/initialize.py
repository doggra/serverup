from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from userland.models import Profile, Customer, Reseller


class Command(BaseCommand):

    def handle(self, *args, **options):

        # Create administrator.
        user = User(username="Administrator", is_staff=True, is_superuser=True)
        user.set_password('admin2017')
        user.save()
        profile = Profile(user=user, account_type=2)
        profile.save()
        admin = user
        print("User {0} crated".format(user.username))

        # Create reseller.
        user = User(username="Reseller")
        user.set_password('resell2017')
        user.save()
        reseller = Reseller.objects.create(user=user, administrator=admin)
        profile = Profile(user=user, account_type=1)
        profile.save()
        reseller = user
        print("User {0} crated".format(user.username))

        # Create customer.
        user = User(username="Customer")
        user.set_password('custom2017')
        user.save()
        customer = Customer.objects.create(user=user, reseller=reseller)
        profile = Profile(user=user, account_type=0)
        profile.save()
        print("User {0} crated".format(user.username))

        # Create customer #2.
        user = User(username="Customer2")
        user.set_password('custom22017')
        user.save()
        customer = Customer.objects.create(user=user, reseller=reseller)
        profile = Profile(user=user, account_type=0)
        profile.save()
        print("User {0} crated".format(user.username))
