#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from bolibana.tools.utils import import_path


@python_2_unicode_compatible
class ReportClass(models.Model):

    REGULAR = 'r'
    INDIVIDUAL = 'i'
    REPORT_TYPES = ((REGULAR, _("Regular")),
                    (INDIVIDUAL, _("Individual")))

    DAY = 'DayPeriod'
    WEEK = 'WeekPeriod'
    MONTH = 'MonthPeriod'
    QUARTER = 'QuarterPeriod'
    YEAR = 'YearPeriod'
    PERIOD_TYPES = (
        (DAY, _("Daily")),
        (WEEK, _("Weekly")),
        (MONTH, _("Monthly")),
        (QUARTER, _("Quarterly")),
        (YEAR, _("Annualy")))

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("Report Class")
        verbose_name_plural = _("Report Classes")

    slug = models.SlugField(_("Slug"), max_length=75, primary_key=True)
    name = models.CharField(_("Name"), max_length=150)
    cls = models.CharField(_("cls"), max_length=75, unique=True)
    period_cls = models.CharField(_("Period Type"), max_length=75,
                                  choices=PERIOD_TYPES)
    report_type = models.CharField(_("Report Type"), max_length=1,
                                   choices=REPORT_TYPES)

    def __str__(self):
        return self.name

    @property
    def period_class(self):
        return import_path('bolibana.models.Period.{}'.format(self.period_cls))

    @property
    def report_class(self):
        return import_path(self.cls)

    @property
    def is_individual(self):
        return self.report_type == self.INDIVIDUAL
