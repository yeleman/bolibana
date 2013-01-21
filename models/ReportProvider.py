#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models
from django.utils.translation import ugettext_lazy as _

SOURCE_LEVEL = 1
AGGREGATED_LEVEL = 2
REPORTING_LEVELS = ((SOURCE_LEVEL, _(u"Source")),
                    (AGGREGATED_LEVEL, _(u"Aggregated")))


class ReportProvider(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Report Provider")
        verbose_name_plural = _(u"Report Providers")
        unique_together = ('project', 'entity')

    project = models.ForeignKey('Project')
    entity = models.ForeignKey('Entity')
    level = models.PositiveIntegerField(choices=REPORTING_LEVELS,
                                        verbose_name=_(u"Reporting Level"))

    def __unicode__(self):
        return (u"%(entity)s/%(project)s:%(level)s"
                % {'entity': self.entity,
                   'project': self.project,
                   'level': self.verbose_level})

    def verbose_level(self):
        for level, name in REPORTING_LEVELS:
            if level == self.level:
                return name
        return u"n/a"

    @classmethod
    def delete_for(cls, entity):
        cls.objects.filter(entity=entity).delete()
