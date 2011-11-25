#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django.shortcuts import render
from django.utils.translation import ugettext as _, ugettext_lazy
from django import forms
from mptt.fields import TreeNodeChoiceField

from bolibana.models import Role, Provider
from bolibana.reporting.models import Entity


class AddressBookForm(forms.Form):

    role = forms.ChoiceField(label=ugettext_lazy(u"Role"), \
                         choices=[('', _(u"All"))] + [(role.slug, role.name) \
                                  for role in Role.objects.all() \
                                                          .order_by('name')])
    entity = TreeNodeChoiceField(queryset=Entity.tree.all(), \
                                 level_indicator=u'---', \
                                 label=ugettext_lazy(u"Entity"))


def addressbook(request, template='addressbook.html'):
    context = {'category': 'addressbook'}

    if request.method == "POST":
        form = AddressBookForm(request.POST)

        providers = Provider.objects.all()

        if request.POST.get('role'):
            providers = providers.filter(access__role__slug=request \
                                 .POST.get('role'))

        if request.POST.get('entity'):
            entity = Entity.objects.get(id=request.POST.get('entity'))
            providers = providers.filter(access__object_id__in=[entity.id] \
                                    + [e.id for e in entity.get_descendants()])
        context.update({'contacts': providers})
    else:
        form = AddressBookForm()

    context.update({'form': form})

    return render(request, template, context)
