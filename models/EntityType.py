#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import implements_to_string
from django.db import models
from django.utils.translation import ugettext_lazy as _


@implements_to_string
class EntityType(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Entity Type")
        verbose_name_plural = _("Entity Types")

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=30)

    def __str__(self):
        return self.name
