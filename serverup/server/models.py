# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import paramiko
import select
import StringIO
from django.db import models
from django.contrib.auth.models import User

OS_DISTRO = (
	(-1, "Unknown"),
	(0, "Debian"),
	(1, "Centos"),
	(2, "Ubuntu"),
)

STATUS = (
	(0, "UP TO DATE"),
	(1, "UPDATES AVAILABLE"),
	(2, "IGNORED"),
	(3, "INSTALL"),
	(4, "ERROR")
)

UPDATE_STATUS = (
	(0, "PENDING"),
	(1, "UPDATED"),
	(2, "IGNORED"),
)


class Package(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return "{}".format(self.package.name,)


class PackageUpdate(models.Model):
	server = models.ForeignKey('Server', on_delete=models.CASCADE)
	package = models.ForeignKey(Package)
	version = models.CharField(max_length=255, blank=True)
	status = models.IntegerField(default=0, choices=UPDATE_STATUS)

	def __unicode__(self):
		return "{} [{}]".format(self.package.name, self.version)


class Server(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
							editable=False, unique=True)
	user = models.ForeignKey(User)
	os = models.IntegerField(null=True, choices=OS_DISTRO)
	ip = models.GenericIPAddressField(default='127.1.1.1')
	ssh_port = models.IntegerField(default=22)
	hostname = models.CharField(max_length=255, default="Unknown")
	status = models.IntegerField(default=3, choices=STATUS)
	public_key = models.TextField(blank=True)
	private_key = models.TextField(blank=True)
	last_check = models.DateTimeField(null=True, blank=True)

	def send_command(self, command):

		ssh = paramiko.SSHClient()
		try:
			# Convert ssh key to readable by paramiko.
			pkey = paramiko.RSAKey.from_private_key(\
										StringIO.StringIO(self.private_key))
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			# Make connection, send command and return response.
			ssh.connect(hostname=self.ip, username='root', pkey=pkey)
			stdin, stdout, stderr = ssh.exec_command(command)
			response = stdout.read()
			return response

		except paramiko.AuthenticationException, e:
			print "Authentication failed when connecting to %s" % self.hostname
			return "FAIL: {}".format(e)

		except Exception, e:
			print "Could not SSH to %s" % self.hostname
			return "FAIL: {}".format(e)

		finally:
			ssh.close()

	def check_updates(self):
		if self.os == 0:
			cmd = "apt-get update -qq && apt-get upgrade -s"
		elif self.os == 1:
			print("Make it betteeeeer!")
			cmd = "yum check-update -q"
		elif self.os == 2:
			cmd = "sudo apt-get update -qq && apt-get upgrade -s"

		r = self.send_command(cmd)

		if "FAIL" in r.decode('utf-8'):
			return r.decode('utf-8')
		else:
			for line in r.splitlines():
				try:
					l = line.decode('utf-8')
					if l.startswith("Inst"):
						l_pieces = l.split(" ")
						pkg_name = l_pieces[1]
						pkg_ver = l_pieces[2].strip("[]")
						pkg, crt = Package.objects.get_or_create(name=pkg_name)
						PackageUpdate.objects.create(server=self,
													 package=pkg,
													 version=pkg_ver)
				except Exception, e:
					return str(e)
			return "OK"

	@property
	def owner(self):
		return self.user.username

	@property
	def show_status(self):
		if self.status == 0:
			return "<span class='badge bg-green'>UPDATED</span>"
		elif self.status == 1:
			count_pending_updates = UpdatePackage.objects.filter(server=self,
																 status=1)\
														 .count()

			return "<span class='badge bg-orange'>{} UPDATES</span>"\
												.format(count_pending_updates,)
		elif self.status == 3:
			return "<span class='badge bg-aqua'>INSTALL</span>"
		elif self.status == 4:
			return "<span class='badge bg-red'>ERROR</span>"

	@property
	def show_os_icon(self):
		if self.os == 0:
			return "<i class='devicon-debian-plain'></i>"
		elif self.os == 1:
			return "<i class='devicon-redhat-plain'></i>"
		else:
			return "?"

	def __unicode__(self):
		return self.ip


class ServerGroup(models.Model):
	name = models.CharField(max_length=20)
	user = models.ForeignKey(User)
	servers = models.ManyToManyField(Server, blank=True)

	@property
	def count_servers(self):
		return self.servers.count()

	def __unicode__(self):
		return self.name
