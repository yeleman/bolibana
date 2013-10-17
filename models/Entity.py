#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
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

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=50)
    type = models.ForeignKey(EntityType, related_name='entities',
                             verbose_name=_("Type"))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name=_("Parent"))
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    objects = TreeManager()

    def __str__(self):
        return self.name

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return ugettext("{name}/{parent}").format(
                name=self.display_name(),
                parent=self.parent.display_name())
        return self.display_name()

    def display_code_name(self):
        return ugettext("{code}/{name}").format(
            code=self.slug, name=self.display_name())

    def parent_level(self):
        if self.parent:
            return self.parent.type
        return self.parent

    @property
    def gps(self):
        if self.latitude is not None and self.longitude is not None:
            return "{lat},{lon}".format(lat=self.latitude, lon=self.longitude)
