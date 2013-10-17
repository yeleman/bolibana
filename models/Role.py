#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import implements_to_string
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bolibana.models.Permission import Permission


@implements_to_string
class Role(models.Model):

    """ A named collection of Permission (not tied to django.auth) """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    permissions = models.ManyToManyField(Permission,
                                         null=True, blank=True,
                                         verbose_name=_("Permissions"))
    level = models.CharField(_("Level"), max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name
