#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _, ugettext
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager


class Entity(MPTTModel):

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Entity")
        verbose_name_plural = _(u"Entities")

    name = models.CharField(_(u"Name"), max_length=50)
    slug = models.SlugField(_(u"Slug"), max_length=15, unique=True)
    type = models.ForeignKey('EntityType', related_name='entities',
                             verbose_name=_(u"Type"))
    phone_number = models.CharField(max_length=12, unique=True,
                                    null=True, blank=True,
                                    verbose_name=_(u"Phone Number"))
    parent = TreeForeignKey('self', null=True, blank=True,
                                                     related_name='children',
                                                     verbose_name=_(u"Parent"))

    objects = TreeManager()

    def __unicode__(self):
        return self.name

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return ugettext(u"%(name)s/%(parent)s") \
                            % {'name': self.display_name(),
                               'parent': self.parent.display_name()}
        return self.display_name()

    def display_code_name(self):
        return ugettext(u"%(code)s/%(name)s") % \
               {'code': self.slug, 'name': self.display_name()}

    def parent_level(self):
        if self.parent:
            return self.parent.type
        return self.parent


@receiver(pre_save, sender=Entity)
def pre_save_entity(sender, instance, **kwargs):
    """ mark phone_number as None is not filled """
    if instance.phone_number == u'':
        instance.phone_number = None
