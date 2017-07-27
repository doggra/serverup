import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from userland.models import Profile

from server.models import Server


UPDATES_DELAY = 30*60 # in seconds
TIME_THRESHOLD = timezone.now()-datetime.timedelta(seconds=UPDATES_DELAY)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(TIME_THRESHOLD)
        servers_to_check = Server.objects\
                                     .filter(last_check__lt=TIME_THRESHOLD)
        for s in servers_to_check:
            s.check_updates()