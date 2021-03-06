#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models
from django.utils.translation import ugettext_lazy as _

from bolibana.tools.utils import import_path


class ReportClass(models.Model):

    REGULAR = 'r'
    INDIVIDUAL = 'i'
    REPORT_TYPES = ((REGULAR, _("Regular")),
                    (INDIVIDUAL, _(u"Individual")))

    DAY = 'DayPeriod'
    WEEK = 'WeekPeriod'
    MONTH = 'MonthPeriod'
    QUARTER = 'QuarterPeriod'
    YEAR = 'YearPeriod'
    PERIOD_TYPES = (
        (DAY, _(u"Daily")),
        (WEEK, _(u"Weekly")),
        (MONTH, _(u"Monthly")),
        (QUARTER, _(u"Quarterly")),
        (YEAR, _(u"Annualy")))

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Report Class")
        verbose_name_plural = _(u"Report Classes")

    slug = models.SlugField(_(u"Slug"), max_length=75, primary_key=True)
    name = models.CharField(_(u"Name"), max_length=150)
    cls = models.CharField(_(u"cls"), max_length=75, unique=True)
    period_cls = models.CharField(_(u"Period Type"), max_length=75,
                                  choices=PERIOD_TYPES)
    report_type = models.CharField(_(u"Report Type"), max_length=1,
                                   choices=REPORT_TYPES)

    def __unicode__(self):
        return self.name

    @property
    def period_class(self):
        return import_path('bolibana.models.Period.%s' % self.period_cls)

    @property
    def report_class(self):
        return import_path(self.cls)

    @property
    def is_individual(self):
        return self.report_type == self.INDIVIDUAL
