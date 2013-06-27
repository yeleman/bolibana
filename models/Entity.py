#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import python_2_unicode_compatible
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from bolibana.models.EntityType import EntityType


@python_2_unicode_compatible
class Entity(MPTTModel):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("Slug"), max_length=15, unique=True)
    type = models.ForeignKey(EntityType, related_name='entities',
                             verbose_name=_("Type"))
    phone_number = models.CharField(max_length=12, unique=True,
                                    null=True, blank=True,
                                    verbose_name=_("Phone Number"))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name=_("Parent"))

    objects = TreeManager()

    def __str__(self):
        return self.name

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return ugettext("%(name)s/%(parent)s") \
                % {'name': self.display_name(),
                   'parent': self.parent.display_name()}
        return self.display_name()

    def display_code_name(self):
        return ugettext("%(code)s/%(name)s") \
            % {'code': self.slug, 'name': self.display_name()}

    def parent_level(self):
        if self.parent:
            return self.parent.type
        return self.parent


@receiver(pre_save, sender=Entity)
def pre_save_entity(sender, instance, **kwargs):
    """ mark phone_number as None is not filled """
    if instance.phone_number == "":
        instance.phone_number = None
