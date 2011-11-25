#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class Role(models.Model):

    """ A named collection of Permission (not tied to django.auth) """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Role")
        verbose_name_plural = _(u"Roles")

    name = models.CharField(_(u"Name"), max_length=50)
    slug = models.SlugField(_(u"Slug"), max_length=15, primary_key=True)
    permissions = models.ManyToManyField('Permission', null=True, blank=True, \
                                         verbose_name=_(u"Permissions"))

    def __unicode__(self):
        return self.name
