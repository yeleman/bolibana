#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import ContentType


class Access(models.Model):
    """ Bundle of a Role for a target object. Usually an Entity.

        Access itself doesn't grant anything. It's just a holder
        Add an access to a Provider instead """

    class Meta:
        app_label = 'bolibana'
        unique_together = ('role', 'content_type', 'object_id')
        verbose_name = _(u"Access")
        verbose_name_plural = _(u"Access")

    role = models.ForeignKey('Role', verbose_name=_(u"Role"))
    # entity
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name()

    def name(self):
        try:
            if self.target.level == 0:
                return self.role.__unicode__()
            else:
                return ugettext(u"%(role)s on %(target)s") \
                                % {'role': self.role, 'target': self.target}
        except ObjectDoesNotExist:
            return u"*Invalid*"

    @classmethod
    def target_data(cls, target):
        ct = ContentType.objects.get_for_model(model=target.__class__)
        oi = target.id
        return (ct, oi)

    @classmethod
    def find_by(cls, role, target):
        ct, oi = cls.target_data(target)
        try:
            return cls.objects.get(role=role, content_type=ct, object_id=oi)
        except cls.DoesNotExist:
            access = cls(role=role, content_type=ct, object_id=oi)
            access.save()
            return access
