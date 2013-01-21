#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class IndividualReport(models.Model):

    """ Applies to an unique target whose not going to be tracked. """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"individual Report")
        verbose_name_plural = _(u"Individual Reports")
        abstract = True

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
    objects = models.Manager()

    def __unicode__(self):
        return ugettext(u"IDVR%(id)d - %(date)s") \
                        % {'id': self.id, \
                           'date': self.created_on.strftime('%d.%m.%Y')}
