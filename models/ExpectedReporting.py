#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models
from django.utils.translation import ugettext_lazy as _

SOURCE_LEVEL = 1
AGGREGATED_LEVEL = 2
REPORTING_LEVELS = ((SOURCE_LEVEL, _(u"Source")),
                    (AGGREGATED_LEVEL, _(u"Aggregated")))


class ExpectedReporting(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Expected Reporting")
        verbose_name_plural = _(u"Expected Reportings")
        unique_together = ('report_class', 'entity', 'period')

    report_class = models.ForeignKey('ReportClass')
    entity = models.ForeignKey('Entity')
    period = models.ForeignKey('Period')
    level = models.PositiveIntegerField(choices=REPORTING_LEVELS,
                                        verbose_name=_(u"Reporting Level"))

    def __unicode__(self):
        return (u"%(entity)s/%(report_class)s:%(level)s"
                % {'entity': self.entity,
                   'report_class': self.report_class,
                   'level': self.verbose_level})

    @property
    def verbose_level(self):
        for level, name in REPORTING_LEVELS:
            if level == self.level:
                return name
        return u"n/a"

    @classmethod
    def delete_for(cls, entity):
        cls.objects.filter(entity=entity).delete()
