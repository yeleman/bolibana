#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import python_2_unicode_compatible

from bolibana.models.BaseReport import BaseReport


@python_2_unicode_compatible
class IndividualReport(BaseReport):

    """ Applies to an unique target whose not going to be tracked.

        """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _("individual Report")
        verbose_name_plural = _("Individual Reports")
        abstract = True

    def __str__(self):
        return ugettext("IDVR%(id)d - %(date)s") \
            % {'id': self.id,
               'date': self.created_on.strftime('%d.%m.%Y')}
