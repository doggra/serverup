from __future__ import absolute_import, unicode_literals
from serverup.celery import app

from .models import Server, PackageUpdate


@app.task()
def task_check_updates(server_uuid):
	s = Server.objects.get(uuid=server_uuid)
	s.check_updates()


@app.task()
def task_update_server(server_uuid):
	s = Server.objects.get(uuid=server_uuid)
	s.update()


@app.task()
def task_update_package(server_uuid, package_name):
	s = Server.objects.get(uuid=server_uuid)
	package = PackageUpdate.objects.get(server__uuid=server_uuid,
										package__name=package_name)
	s.update(package=package)
