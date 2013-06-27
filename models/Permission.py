#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Permission(models.Model):

    """ A slug representing a permission. Not tied to django.auth """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")

    slug = models.SlugField(_("Slug"), max_length=50, primary_key=True)

    def __str__(self):
        return self.slug
