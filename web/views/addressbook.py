#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django import forms

from mptt.fields import TreeNodeChoiceField

from bolibana.models.Role import Role
from bolibana.models.Provider import Provider
from bolibana.models.Entity import Entity
from bolibana.web.decorators import provider_permission

from nosmsd.utils import send_sms


class AddressBookForm(forms.Form):

    role = forms.ChoiceField(label=ugettext_lazy("Role"),
                             choices=[('', _("All"))] + [(role.slug, role.name)
                                                         for role in Role.objects.all()
                                                                         .order_by('name')])
    entity = TreeNodeChoiceField(queryset=Entity.objects.all(),
                                 level_indicator='---',
                                 label=ugettext_lazy("Entity"))


class MessageForm(forms.Form):

    text = forms.CharField(widget=forms.Textarea(), label=("Texte"))

    def clean_text(self):
        return self.cleaned_data.get('text')[:150]


def addressbook(request, template='addressbook.html'):
    context = {'category': 'addressbook'}

    if request.method == "POST":
        form = AddressBookForm(request.POST)
        form_msg = MessageForm()

        providers = Provider.objects.all()

        if request.POST.get('role'):
            providers = providers.filter(access__role__slug=request
                                 .POST.get('role'), is_active=True)

        if request.POST.get('entity'):
            entity = Entity.objects.get(id=request.POST.get('entity'))
            providers = providers.filter(access__object_id__in=[entity.id]
                                         + [e.id for e in entity.get_descendants()],
                                         is_active=True)

        context.update({'contacts': providers})
    else:
        form_msg = MessageForm()
        form = AddressBookForm()

    context.update({'form': form, 'form_msg': form_msg})

    return render(request, template, context)


@provider_permission('can_monitor_transmission')
def adressbook_send_sms(request):
    if request.method == "POST":
        form_msg = MessageForm(request.POST)
        providers = Provider.objects.filter(is_active=True)

        role_slug = request.POST.get('role', None)
        try:
            entity_id = int(request.POST.get('entity', 1))
        except TypeError:
            entity_id = 1

        if role_slug:
            providers = providers.filter(access__role__slug=request
                                 .POST.get('role'), is_active=True)

        if entity_id:
            entity = Entity.objects.get(id=entity_id)
            providers = providers.filter(access__object_id__in=[entity.id]
                                         + [e.id for e in entity.get_descendants()],
                                         is_active=True)

        is_everything = not role_slug and entity_id == 1

        if form_msg.is_valid() and not is_everything:
            for provider in providers:
                send_sms(provider.phone_number,
                         form_msg.cleaned_data.get('text'))
            messages.success(request,
                             _("SMS en cours d'envoie à {} destinataires")
                             .format(providers.count()))
            return redirect("log_message")
        else:
            messages.error(request,
                           _("SMS non envoyé : Vous demandez"
                             "d'envoyer un SMS a tous les utisateurs"))
            return redirect(addressbook)
