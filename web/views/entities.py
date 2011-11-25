#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import logging

from django.forms import ModelForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import ListView

from bolibana.reporting.models import Entity
from bolibana.tools.decorators import provider_permission

logger = logging.getLogger(__name__)


class EntitiesListView(ListView):
    """ Generic List View for Providers """

    context_object_name = 'entities_list'
    template_name = 'entities_list.html'

    def get_queryset(self):
        return Entity.objects.order_by('slug')

    def get_context_data(self, **kwargs):
        context = super(EntitiesListView, self).get_context_data(**kwargs)
        # Add category
        context['category'] = 'entities'
        return context


class AddEntityForm(ModelForm):

    class Meta:
        model = Entity


class EditEntityForm(ModelForm):

    class Meta:
        model = Entity
        exclude = ('slug',)


@provider_permission('can_manage_entities')
def add_edit_entity(request, entity_id=None, template='add_edit_entity.html'):
    context = {'category': 'entities'}

    if entity_id:
        entity = get_object_or_404(Entity, id=entity_id)
        formclass = EditEntityForm
    else:
        entity = None
        formclass = AddEntityForm

    if request.method == 'POST':

        form = formclass(request.POST, instance=entity)
        if form.is_valid():
            entity = form.save()
            if entity_id:
                message = _(u"Entity %(entity)s updated.") \
                          % {'entity': entity.display_full_name()}
            else:
                message = _(u"Entity %(entity)s created.") \
                          % {'entity': entity.display_full_name()}
            messages.success(request, message)
            return redirect('list_entities')
        else:
            pass

    # GET METHOD
    else:
        form = formclass(instance=entity)

    context.update({'form': form, 'entity_id': entity_id, 'entity': entity})

    return render(request, template, context)
