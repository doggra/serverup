from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from userland.models import Profile
from history.models import EventType

class Command(BaseCommand):

    def handle(self, *args, **options):
        EventType.objects.create(name="SSH Command execution")
