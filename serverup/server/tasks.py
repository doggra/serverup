from __future__ import absolute_import, unicode_literals
from serverup.celery import app

from .models import Server


@app.task()
def task_check_updates(server_uuid):
	s = Server.objects.get(uuid=server_uuid)
	s.check_updates()


@app.task()
def task_update_server(server_uuid, package=None):
	s = Server.objects.get(uuid=server_uuid)
	s.update(package=package)
