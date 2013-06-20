#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import reversion
from django.dispatch import receiver
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _, ugettext


def unvalidated_status():
    return (Report.STATUS_UNSAVED,
            Report.STATUS_CREATED,
            Report.STATUS_INCOMPLETE,
            Report.STATUS_ERRONEOUS,
            Report.STATUS_COMPLETE,
            Report.STATUS_MODIFIED_AUTHOR,
            Report.STATUS_MODIFIED_VALIDATOR)

def validated_status():
    return (Report.STATUS_VALIDATED,
            Report.STATUS_CLOSED,
            Report.STATUS_AUTO_VALIDATED)

def complete_status():
    return (Report.STATUS_COMPLETE,
            Report.STATUS_VALIDATED,
            Report.STATUS_CLOSED,
            Report.STATUS_MODIFIED_AUTHOR,
            Report.STATUS_MODIFIED_VALIDATOR,
            Report.STATUS_AUTO_VALIDATED)


class ValidationMixin(object):
    def unvalidated(self):
        return self.filter(_status__in=unvalidated_status())

    def validated(self):
        return self.filter(_status__in=validated_status())

    def complete(self):
        return self.filter(_status__in=complete_status())

class ValidationQuerySet(QuerySet, ValidationMixin):
    pass

class ValidationManager(models.Manager, ValidationMixin):
    def get_query_set(self):
        return ValidationQuerySet(self.model, using=self._db)


class UnValidatedManager(models.Manager):

    def get_query_set(self):
        return super(UnValidatedManager, self).get_query_set() \
                        .filter(_status__in=unvalidated_status())


class ValidatedManager(models.Manager):

    def get_query_set(self):
        return super(ValidatedManager, self).get_query_set() \
                        .filter(_status__in=validated_status())


class CompleteManager(models.Manager):

    def get_query_set(self):
        return super(CompleteManager, self).get_query_set() \
                        .filter(_status__in=complete_status())


class Report(models.Model):

    """ Applies to period-entity dependent report. """

    STATUS_UNSAVED = 0
    STATUS_CREATED = 1
    STATUS_INCOMPLETE = 2
    STATUS_ERRONEOUS = 3
    STATUS_COMPLETE = 4
    STATUS_VALIDATED = 5
    STATUS_CLOSED = 6
    # NUT Additions
    STATUS_MODIFIED_AUTHOR = 7
    STATUS_MODIFIED_VALIDATOR = 8
    STATUS_AUTO_VALIDATED = 9

    STATUSES = ((STATUS_CREATED, u"Created"),
                (STATUS_MODIFIED_AUTHOR, u"Modified by author"),
                (STATUS_MODIFIED_VALIDATOR, u"Modified by validator"),
                (STATUS_AUTO_VALIDATED, u"Auto-validated"),
                (STATUS_VALIDATED, u"Validated"))
    STATUSES = ((STATUS_UNSAVED, u"Unsaved"),
                (STATUS_CREATED, u"Created"),
                (STATUS_INCOMPLETE, u"Incomplete"),
                (STATUS_ERRONEOUS, u"Erroneous"),
                (STATUS_COMPLETE, u"Complete"),
                (STATUS_VALIDATED, u"Validated"),
                (STATUS_CLOSED, u"Closed"),
                (STATUS_MODIFIED_AUTHOR, u"Modified by author"),
                (STATUS_MODIFIED_VALIDATOR, u"Modified by validator"),
                (STATUS_AUTO_VALIDATED, u"Auto-validated"))
    STATUSES_STR = {
        STATUS_UNSAVED: 'STATUS_UNSAVED',
        STATUS_CREATED: 'STATUS_CREATED',
        STATUS_INCOMPLETE: 'STATUS_INCOMPLETE',
        STATUS_ERRONEOUS: 'STATUS_ERRONEOUS',
        STATUS_COMPLETE: 'STATUS_COMPLETE',
        STATUS_VALIDATED: 'STATUS_VALIDATED',
        STATUS_CLOSED: 'STATUS_CLOSED',
        STATUS_MODIFIED_AUTHOR: 'STATUS_MODIFIED_AUTHOR',
        STATUS_MODIFIED_VALIDATOR: 'STATUS_MODIFIED_VALIDATOR',
        STATUS_AUTO_VALIDATED: 'STATUS_AUTO_VALIDATED',
    }

    TYPE_SOURCE = 0
    TYPE_AGGREGATED = 1
    TYPES = ((TYPE_SOURCE, _(u"Source")), (TYPE_AGGREGATED, _(u"Aggregated")))

    TYPES_STR = {
        TYPE_SOURCE: 'TYPE_SOURCE',
        TYPE_AGGREGATED: 'TYPE_AGGREGATED'
    }

    class Meta:
        app_label = 'bolibana'
        unique_together = ('period', 'entity', 'type')
        verbose_name = _(u"Report")
        verbose_name_plural = _(u"Reports")
        abstract = True

    _status = models.PositiveIntegerField(choices=STATUSES, \
                                          default=STATUS_CREATED, \
                                          verbose_name=_(u"Status"))
    type = models.PositiveIntegerField(choices=TYPES, verbose_name=_(u"Type"))
    receipt = models.CharField(max_length=30, unique=True, \
                               blank=True, null=False, \
                               verbose_name=_(u"Receipt"))
    period = models.ForeignKey('Period',
                               related_name='%(app_label)s_' \
                                            '%(class)s_reports',
                               verbose_name=_(u"Period"))
    entity = models.ForeignKey('Entity',
                               related_name='%(app_label)s_' \
                                            '%(class)s_reports',
                               verbose_name=_(u"Entity"))
    created_by = models.ForeignKey('Provider', \
                                   related_name='%(app_label)s_' \
                                                '%(class)s_reports',
                                   verbose_name=_(u"Created By"))
    created_on = models.DateTimeField(auto_now_add=True, \
                                      verbose_name=_(u"Created On"))
    modified_by = models.ForeignKey('Provider', \
                                    null=True, blank=True, \
                                    verbose_name=_(u"Modified By"))
    modified_on = models.DateTimeField(auto_now=True, \
                                       verbose_name=_(u"Modified On"))

    # django manager first
    objects = ValidationManager() # models.Manager()
    unvalidated = UnValidatedManager()
    validated = ValidatedManager()
    complete = CompleteManager()

    def __unicode__(self):
        return ugettext(u"%(entity)s/%(period)s") % {'entity': self.entity, \
                                           'period': self.period}

    @classmethod
    def create(cls, period, entity, author, *args, **kwargs):
        """ create a blank report filling all non-required fields """
        report = cls(period=period, entity=entity, created_by=author, \
                     modified_by=author, _status=cls.STATUS_UNSAVED)
        for arg, value in kwargs.items():
            try:
                setattr(report, arg, value)
            except AttributeError:
                pass
        report.save()

    def validate(self):
        pass

    def status(self):
        return self._status

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
                  % {'day': instance.created_on.strftime('%j'), \
                     'dow': DOW[int(instance.created_on.strftime('%w'))], \
                     'entity': instance.entity.slug, \
                     'id': instance.id, \
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
