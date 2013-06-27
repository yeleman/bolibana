#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.encoding import python_2_unicode_compatible

from bolibana.models.Role import Role


@python_2_unicode_compatible
class Access(models.Model):
    """ Bundle of a Role for a target object. Usually an Entity.

        Access itself doesn't grant anything. It's just a holder
        Add an access to a Provider instead """

    class Meta:
        app_label = 'bolibana'
        unique_together = ('role', 'content_type', 'object_id')
        verbose_name = _("Access")
        verbose_name_plural = _("Access")

    role = models.ForeignKey(Role, verbose_name=_("Role"))
    # entity
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name()

    def name(self):
        try:
            if getattr(self.target, 'level', -1) == 0:
                return str(self.role)
            else:
                return ugettext("%(role)s on %(target)s") \
                    % {'role': self.role, 'target': self.target}
        except ObjectDoesNotExist:
            return "*Invalid*"

    @classmethod
    def target_data(cls, target):
        ct = ContentType.objects.get_for_model(model=target.__class__)
        oi = target.id
        return (ct, oi)

    @classmethod
    def find_by(cls, role, target):
        ct, oi = cls.target_data(target)
        try:
            return cls.objects.get(role=role, content_type=ct, object_id=oi)
        except cls.DoesNotExist:
            access = cls(role=role, content_type=ct, object_id=oi)
            access.save()
            return access
