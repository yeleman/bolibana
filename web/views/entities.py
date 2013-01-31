#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import logging

from django.forms import ModelForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import ListView

from bolibana.models.Entity import Entity
from bolibana.models.ScheduledReporting import ScheduledReporting
from bolibana.models.ReportClass import ReportClass
from bolibana.models.ExpectedReporting import SOURCE_LEVEL
from bolibana.web.decorators import provider_permission

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

    def clean_phone_number(self):
        if not self.cleaned_data.get('phone_number'):
            return None


class AddScheduledReportingForm(ModelForm):
        class Meta:
            model = ScheduledReporting
            exclude = ['report_class', 'entity', ]

        def clean_level(self):
            """ if not level return -1 """
            if self.cleaned_data.get('level') is None:
                return -1
            return self.cleaned_data.get('level')


class EditEntityForm(ModelForm):

    class Meta:
        model = Entity
        exclude = ('slug',)


@provider_permission('can_manage_entities')
def add_edit_entity(request, entity_id=None, template='add_edit_entity.html'):
    context = {'category': 'entities'}
    report_classes = ReportClass.objects.all()
    scheduled_forms = []

    if entity_id:
        entity = get_object_or_404(Entity, id=entity_id)

        for report_class in report_classes:
            try:
                ScheduledReporting.objects.get(report_class=report_class,
                                               entity=entity)
            except:
                scheduled = ScheduledReporting(report_class=report_class,
                                               entity=entity)
                scheduled.level = SOURCE_LEVEL
                scheduled.save()
        for scheduled in ScheduledReporting.objects.filter(entity=entity):
            scheduled_form = AddScheduledReportingForm(instance=scheduled)
            scheduled_forms.append(scheduled_form)
        formclass = EditEntityForm
    else:
        entity = None
        formclass = AddEntityForm

    if request.method == 'POST':
        form = formclass(request.POST, instance=entity)
        # edit entity
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

        # edit scheduled
        if 'scheduled_id' in request.POST:
            scheduled_form = AddScheduledReportingForm(request.POST)
            try:
                scheduled_id = int(request.POST.get('scheduled_id', 0))
            except ValueError:
                scheduled_id = 0
            try:
                scheduled = ScheduledReporting.objects.get(id=scheduled_id)
            except:
                pass
            if scheduled_form.is_valid():
                level = scheduled_form.cleaned_data.get('level')

                start = scheduled_form.cleaned_data.get('start')
                end = scheduled_form.cleaned_data.get('end')

                scheduled.level = level
                scheduled.start = start
                scheduled.end = end
                scheduled.save()
                message = _(u"Reporting activities of this Entity have" \
                            u" been updated.")
                messages.success(request, message)
                return redirect(add_edit_entity, entity_id=entity_id)
            else:
                context.update({'fake_instance': scheduled})
                for i, f in enumerate(scheduled_forms):
                    if f.instance.id == scheduled_id:
                        scheduled_forms[i] = scheduled_form
                        break
                form = formclass(instance=entity)
        else:
            pass

    # GET METHOD
    else:
        form = formclass(instance=entity)
    context.update({'form': form, 'entity_id': entity_id, 'entity': entity,
                    'scheduled_forms': scheduled_forms})

    return render(request, template, context)
