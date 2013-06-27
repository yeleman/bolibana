#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from bolibana.models.ReportClass import ReportClass
from bolibana.models.Entity import Entity
from bolibana.models.Period import Period

SOURCE_LEVEL = 1
AGGREGATED_LEVEL = 2
REPORTING_LEVELS = ((SOURCE_LEVEL, _("Source")),
                    (AGGREGATED_LEVEL, _("Aggregated")))


@python_2_unicode_compatible
class ExpectedReporting(models.Model):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Expected Reporting")
        verbose_name_plural = _("Expected Reportings")
        unique_together = ('report_class', 'entity', 'period')

    report_class = models.ForeignKey(ReportClass)
    entity = models.ForeignKey(Entity)
    period = models.ForeignKey(Period)
    level = models.PositiveIntegerField(choices=REPORTING_LEVELS,
                                        verbose_name=_("Reporting Level"))

    def __self__(self):
        return ("%(entity)s/%(report_class)s:%(level)s"
                % {'entity': self.entity,
                   'report_class': self.report_class,
                   'level': self.verbose_level})

    @property
    def verbose_level(self):
        for level, name in REPORTING_LEVELS:
            if level == self.level:
                return name
        return "n/a"

    @classmethod
    def delete_for(cls, entity):
        cls.objects.filter(entity=entity).delete()
