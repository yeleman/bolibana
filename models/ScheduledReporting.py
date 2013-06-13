#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ExpectedReporting import REPORTING_LEVELS


class ScheduledReporting(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Scheduled Reporting")
        verbose_name_plural = _(u"Scheduled Reporting")
        unique_together = ('report_class', 'entity')

    report_class = models.ForeignKey('ReportClass')
    entity = models.ForeignKey('Entity')
    level = models.PositiveIntegerField(choices=REPORTING_LEVELS,
                                        verbose_name=_(u"Reporting Level"),
                                        blank=False, null=False)
    start = models.ForeignKey('Period',
                              verbose_name=_(u"Start On"),
                              related_name='entity_rcls_providers_starting',
                              null=True, blank=True)
    end = models.ForeignKey('Period',
                            verbose_name=_(u"End On"),
                            related_name='entity_rcls_providers_ending',
                            null=True, blank=True)

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

    @property
    def casted_start(self):
        try:
            return self.report_class.period_class \
                .find_create_with(start_on=self.start.start_on,
                                  end_on=self.start.end_on)
        except:
            return None

    @property
    def casted_end(self):
        try:
            return self.report_class.period_class \
                .find_create_with(start_on=self.end.start_on,
                                  end_on=self.end.end_on)
        except:
            return None
