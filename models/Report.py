#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _, ugettext

from bolibana.models.BaseReport import BaseReport


class Report(BaseReport):

    """ Applies to period-entity dependent report. """

    TYPE_SOURCE = 'TYPE_SOURCE'
    TYPE_AGGREGATED = 'TYPE_AGGREGATED'
    TYPES = ((TYPE_SOURCE, _(u"Source")), (TYPE_AGGREGATED, _(u"Aggregated")))

    class Meta:
        app_label = 'bolibana'
        unique_together = ('period', 'entity', 'type')
        verbose_name = _(u"Report")
        verbose_name_plural = _(u"Reports")
        abstract = True

    type = models.CharField(max_length=30, choices=TYPES, verbose_name=_(u"Type"))
    receipt = models.CharField(max_length=30, unique=True,
                               blank=True, null=False,
                               verbose_name=_(u"Receipt"))
    period = models.ForeignKey('Period',
                               related_name='%(app_label)s_'
                                            '%(class)s_reports',
                               verbose_name=_(u"Period"))
    entity = models.ForeignKey('Entity',
                               related_name='%(app_label)s_'
                                            '%(class)s_reports',
                               verbose_name=_(u"Entity"))

    def __unicode__(self):
        return ugettext(u"%(entity)s/%(period)s") \
            % {'entity': self.entity,
               'period': self.period}

    @classmethod
    def create(cls, period, entity, author, *args, **kwargs):
        """ create a blank report filling all non-required fields """
        report = cls(period=period, entity=entity, created_by=author,
                     modified_by=author, _status=cls.STATUS_UNSAVED)
        for arg, value in kwargs.items():
            try:
                setattr(report, arg, value)
            except AttributeError:
                pass
        report.save()

    @classmethod
    def generate_receipt(cls, instance):
        """ generates a reversable text receipt for a Report

        FORMAT:
            000/sss-111-D
            000: internal report ID
            sss: entity slug
            111: sent day in year
            D: sent day of week """

        DOW = ['D', 'L', 'M', 'E', 'J', 'V', 'S']

        receipt = '%(id)d/%(entity)s-%(day)s-%(dow)s' \
                  % {'day': instance.created_on.strftime('%j'),
                     'dow': DOW[int(instance.created_on.strftime('%w'))],
                     'entity': instance.entity.slug,
                     'id': instance.id,
                     'period': instance.period.id}
        return receipt


@receiver(pre_save, sender=Report)
def pre_save_report(sender, instance, **kwargs):
    """ change _status property of Report on save() at creation """
    if instance._status == instance.STATUS_UNSAVED:
        instance._status = instance.STATUS_CLOSED
    # following will allow us to detect failure in registration
    if not instance.receipt:
        instance.receipt = 'NO_RECEIPT'


@receiver(post_save, sender=Report)
def post_save_report(sender, instance, **kwargs):
    """ generates the receipt """
    if instance.receipt == 'NO_RECEIPT':
        instance.receipt = sender.generate_receipt(instance)
        instance.save()
