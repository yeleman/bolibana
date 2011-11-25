#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class Permission(models.Model):

    """ A slug representing a permission. Not tied to django.auth """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Permission")
        verbose_name_plural = _(u"Permissions")

    slug = models.SlugField(_(u"Slug"), max_length=50, primary_key=True)

    def __unicode__(self):
        return self.slug
