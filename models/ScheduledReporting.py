#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import implements_to_string
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bolibana.models.ExpectedReporting import REPORTING_LEVELS
from bolibana.models.Entity import Entity
from bolibana.models.ReportClass import ReportClass
from bolibana.models.Period import Period


@implements_to_string
class ScheduledReporting(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Scheduled Reporting")
        verbose_name_plural = _("Scheduled Reporting")
        unique_together = ('report_class', 'entity')

    report_class = models.ForeignKey(ReportClass)
    entity = models.ForeignKey(Entity)
    level = models.PositiveIntegerField(choices=REPORTING_LEVELS,
                                        verbose_name=_("Reporting Level"),
                                        blank=False, null=False)
    start = models.ForeignKey(Period,
                              verbose_name=_("Start On"),
                              related_name='entity_rcls_providers_starting',
                              null=True, blank=True)
    end = models.ForeignKey(Period,
                            verbose_name=_("End On"),
                            related_name='entity_rcls_providers_ending',
                            null=True, blank=True)

    def __str__(self):
        return "{entity}/{report_class}:{level}".format(
            entity=self.entity,
            report_class=self.report_class,
            level=self.verbose_level)

    @property
    def verbose_level(self):
        for level, name in REPORTING_LEVELS:
            if level == self.level:
                return name
        return "n/a"

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
