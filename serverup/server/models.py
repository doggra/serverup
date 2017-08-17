# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import time
import uuid
import paramiko
import select
import StringIO
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from history.models import Event

OS_DISTRO = (
    (0, "Debian"),
    (1, "Centos"),
)

STATUS = (
    (0, "UP TO DATE"),
    (1, "UPDATES AVAILABLE"),
    (2, "PENDING"),
    (3, "INSTALL"),
    (4, "ERROR")
)

class Package(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "{}".format(self.name,)


class PackageUpdate(models.Model):
    user = models.ForeignKey(User, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey('Server', on_delete=models.CASCADE)
    package = models.ForeignKey(Package)
    version = models.CharField(max_length=255, blank=True)
    ignore = models.BooleanField(default=False)

    def __unicode__(self):
        return "{} [{}]".format(self.package.name, self.version)

    @property
    def check_ignore(self):
        """ Return checked to HTML input (checkbox) """
        return "checked" if not self.ignore else ""

    @property
    def show_status(self):
        if self.status == 0:
            return "<span class='badge bg-orange'>PENDING</span>"
        elif self.status == 1:
            return "<span class='badge bg-green'>UPDATED</span>"
        elif self.status == 2:
            return "<span class='badge bg-red'>IGNORED</span>"


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
    auto_updates = models.BooleanField(default=True)
    update_interval = models.PositiveIntegerField(default=24) # in hours


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
            Event.objects.create(info=response, extra_info=command, server=self)
            return response

        except paramiko.AuthenticationException, e:
            print "Authentication failed when connecting to %s" % self.hostname
            return "FAIL: {}".format(e)

        except Exception, e:
            print "Could not SSH to %s" % self.hostname
            return "FAIL: {}".format(e)

        finally:
            ssh.close()

    def update(self, package=None):
        """ Function for updating packages
        """
        if package:
            query = package
            to_update = package.package.name
        else:
            query = PackageUpdate.objects.filter(server=self, ignore=False)
            to_update = " ".join(list(query.values_list('package__name',
                                                                flat=True)))

        if self.os == 0:
            cmd = "apt-get install --only-upgrade {}".format(to_update,)
        elif self.os == 1:
            cmd = "yum update -y {}".format(to_update,)

        r = self.send_command(cmd)

        print(r)
        # TODO: Condition - if everything was OK.

        query.delete()
        if PackageUpdate.objects.filter(server=self, ignore=False).count() == 0:
            self.status = 0
        self.save()

    def check_updates(self, auto_update=False):
        if self.os == 0:
            cmd = "apt-get update -qq && apt-get upgrade -s"
        elif self.os == 1:
            cmd = "yum check-update -q"

        r = self.send_command(cmd)
        print(r)

        pkg_pack = []
         
        # Parse output and save results.
        for line in r.splitlines():
            package = version = None

            # Get package updates for Debian.
            if self.os == 0:
                l = line.decode('utf-8')
                if l.startswith("Inst"):
                    l_pieces = l.split(" ")
                    package = l_pieces[1]
                    version = l_pieces[2].strip("[]")

            # Get package updates for CentOS.
            elif self.os == 1:
                m = re.search(r'([:+\w\._-]+)\s+([:+\w\._-]+)', line)
                if m:
                    package = m.group(1)
                    version = m.group(2)

            # Save package update in DB.
            if package and version:
                pkg, crt = Package.objects.get_or_create(name=package)
                pkg_upt, crt = PackageUpdate.objects\
                                                .get_or_create(user=self.user,
                                                               server=self,
                                                               package=pkg,
                                                               version=version)
                pkg_pack.append(pkg_upt)

            else:
                pass
                # TODO Report error (no version or package name ?)

        # Set server pending status if new updates available.
        if len(pkg_pack) > 0:
            self.status = 1

        # Set updated status if no new updates.
        elif len(pkg_pack) == 0:
            self.status = 0

        self.last_check = datetime.datetime.now()
        self.save()
        return r

    def toggle_auto_updates(self):
        self.auto_updates = True if self.auto_updates == False else False
        self.save()

    @property
    def owner(self):
        return self.user.username

    @property
    def show_status(self):
        """ Display HTML status.
        """
        if self.status == 0:
            return "<span class='badge bg-green'>UPDATED</span>"
        elif self.status == 1:
            pending_updates = PackageUpdate.objects.filter(server=self,
                                                           ignore=False)
            c_pending = pending_updates.count()

            return "<span class='badge bg-orange'>{} UPDATES</span>"\
                                                .format(c_pending,)
        elif self.status == 2:
            return "<span class='badge bg-orange'>PENDING</span>"
        elif self.status == 3:
            return "<span class='badge bg-aqua'>INSTALL</span>"
        elif self.status == 4:
            return "<span class='badge bg-red'>ERROR</span>"

    @property
    def show_os_icon(self):
        """ Display HTML icon of OS distribution.
        """
        if self.os == 0:
            return "<i class='devicon-debian-plain'></i>"
        elif self.os == 1:
            return "<i class='devicon-redhat-plain'></i>"
        else:
            return "?"

    def delete(self):
        r = self.send_command('/usr/local/bin/serverup-uninstall')
        print(r)
        super(Server, self).delete()

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
