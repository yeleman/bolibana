#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import python_2_unicode_compatible

from bolibana.tools.utils import generate_user_hash
from bolibana.models.Access import Access


class ActiveManager(models.Manager):

    def get_query_set(self):
        return super(ActiveManager, self).get_query_set() \
                                         .filter(is_active=True)


@python_2_unicode_compatible
class Provider(AbstractUser):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")

    phone_number = models.CharField(max_length=12, unique=True,
                                    null=True, blank=True,
                                    verbose_name=_("Phone Number"))
    phone_number_extra = models.CharField(max_length=12,
                                          null=True, blank=True,
                                          verbose_name=_("Phone Number"))
    access = models.ForeignKey(Access, null=False, blank=False,
                               verbose_name=_("Access"))
    # password hash is an optionnal shorter form of the encrypted password
    # used in size-limted (SMS) environment.
    pwhash = models.CharField(max_length=255,
                              null=True, blank=True,
                              verbose_name=_("Password Hash"))

    # django manager first
    objects = UserManager()
    active = ActiveManager()

    def __str__(self):
        return self.name()

    def name(self):
        """ prefered representation of the provider's name """
        if self.first_name and self.last_name:
            return "{first} {last}".format(
                first=self.first_name.title(),
                last=self.last_name.title())
        if self.first_name:
            return self.first_name.title()

        if self.last_name:
            return self.last_name.title()

        return self.username

    def name_access(self):
        if self.access:
            return ugettext("{name} ({access})").format(
                name=self.name(),
                access=self.access.name())
        else:
            return self.name()

    def to_dict(self):
        return {'first_name': self.first_name, 'last_name': self.last_name,
                'username': self.username, 'phone_number': self.phone_number,
                'email': self.email,
                'phone_number_extra': self.phone_number_extra}

    @classmethod
    def create_provider(cls, username, password,
                        phone_number=None, access=None):
        """ shortcut creation of provider with its associated User """
        provider, created = cls.objects.get_or_create(username=username,
                                                      password=password,
                                                      access=access)
        provider.phone_number = phone_number
        provider.pwhash = cls.generate_hash(username, password)
        provider.save()
        return provider

    def has_permission(self, perm_slug, entity=None):
        """ whether or not User has this permission for Enitity """
        if entity is not None:
            if self.target() is None:
                return False
            if not entity in [entity] + self.target().get_descendants():
                return False

        if self.role() is None:
                return False

        if perm_slug in [p.slug for p in self.role().permissions.all()]:
            return True
        return False

    def role(self):
        """ only or main role if Provider has many """
        try:
            return self.access.role
        except AttributeError:
            return None

    def target(self):
        try:
            return self.access.target
        except AttributeError:
            return None

    def check_hash(self, pwhash):
        return self.pwhash == pwhash

    @classmethod
    def generate_hash(cls, username, password):
        return generate_user_hash(username, password)

    # this one is not a proxy
    def get_full_name(self):
        return self.name()
