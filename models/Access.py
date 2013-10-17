#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import implements_to_string
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext

from bolibana.models.Role import Role
from bolibana.models.Entity import Entity


@implements_to_string
class Access(models.Model):
    """ Bundle of a Role for a target object. Usually an Entity.

        Access itself doesn't grant anything. It's just a holder
        Add an access to a Provider instead """

    class Meta:
        app_label = 'bolibana'
        unique_together = ('role', 'target')
        verbose_name = _("Access")
        verbose_name_plural = _("Access")

    role = models.ForeignKey(Role, verbose_name=_("Role"))
    target = models.ForeignKey(Entity, verbose_name=_("Entity"))

    def __str__(self):
        return self.name()

    def name(self):
        try:
            if getattr(self.target, 'level', -1) == 0:
                return "{role}".format(role=self.role)
            else:
                return ugettext("{role} on {target}").format(
                    role=str(self.role), target=str(self.target))
        except ObjectDoesNotExist:
            return "*Invalid*"

    @classmethod
    def find_by(cls, role, target):
        try:
            return cls.objects.get(role=role, target=target)
        except cls.DoesNotExist:
            access = cls(role=role, target=target)
            access.save()
            return access
