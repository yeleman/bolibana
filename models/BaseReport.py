#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _


def unvalidated_status():
    return (BaseReport.STATUS_UNSAVED,
            BaseReport.STATUS_CREATED,
            BaseReport.STATUS_INCOMPLETE,
            BaseReport.STATUS_ERRONEOUS,
            BaseReport.STATUS_COMPLETE,
            BaseReport.STATUS_MODIFIED_AUTHOR,
            BaseReport.STATUS_MODIFIED_VALIDATOR)


def validated_status():
    return (BaseReport.STATUS_VALIDATED,
            BaseReport.STATUS_CLOSED,
            BaseReport.STATUS_AUTO_VALIDATED)


def complete_status():
    return (BaseReport.STATUS_COMPLETE,
            BaseReport.STATUS_VALIDATED,
            BaseReport.STATUS_CLOSED,
            BaseReport.STATUS_MODIFIED_AUTHOR,
            BaseReport.STATUS_MODIFIED_VALIDATOR,
            BaseReport.STATUS_AUTO_VALIDATED)


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


class BaseReport(models.Model):

    STATUS_UNSAVED = 'STATUS_UNSAVED'
    STATUS_CREATED = 'STATUS_CREATED'
    STATUS_INCOMPLETE = 'STATUS_INCOMPLETE'
    STATUS_ERRONEOUS = 'STATUS_ERRONEOUS'
    STATUS_COMPLETE = 'STATUS_COMPLETE'
    STATUS_VALIDATED = 'STATUS_VALIDATED'
    STATUS_CLOSED = 'STATUS_CLOSED'
    # NUT Additions
    STATUS_MODIFIED_AUTHOR = 'STATUS_MODIFIED_AUTHOR'
    STATUS_MODIFIED_VALIDATOR = 'STATUS_MODIFIED_VALIDATOR'
    STATUS_AUTO_VALIDATED = 'STATUS_AUTO_VALIDATED'

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

    class Meta:
        app_label = 'bolibana'
        abstract = True

    # Status regarding validation
    _status = models.CharField(max_length=30,
                               choices=STATUSES,
                               default=STATUS_CREATED,
                               verbose_name=_(u"Status"))

    # Provider who created report. never altered.
    created_by = models.ForeignKey('Provider',
                                   related_name='%(app_label)s_'
                                                '%(class)s_reports',
                                   verbose_name=_(u"Created By"))
    # date of creation. Never altered.
    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_(u"Created On"))

    # last Provider who edited report. Initialized with created_by
    modified_by = models.ForeignKey('Provider',
                                    null=True, blank=True,
                                    verbose_name=_(u"Modified By"))
    # last time report was editer. Initialized with created_on
    modified_on = models.DateTimeField(auto_now=True,
                                       verbose_name=_(u"Modified On"))

    # django manager first
    objects = ValidationManager()  # models.Manager()
    unvalidated = UnValidatedManager()
    validated = ValidatedManager()
    complete = CompleteManager()
    django = models.Manager()

    def validate(self):
        pass

    def status(self):
        return self._status

    @classmethod
    def create(cls, *args, **kwargs):
        return cls.django.create(*args, **args)
