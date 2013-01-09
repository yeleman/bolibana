#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    name = models.CharField(_(u"Name"), max_length=30)
    slug = models.SlugField(_(u"Slug"), max_length=15, unique=True)

    def __unicode__(self):
        return self.name
