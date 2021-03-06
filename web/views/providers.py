#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import logging

from django import forms
from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.views.generic import ListView
from mptt.fields import TreeNodeChoiceField

from bolibana.models import Role, Provider, Access
from bolibana.auth.utils import (username_from_name, random_password,
                                 random_sample_password)
from bolibana.models import Entity
from bolibana.tools.utils import send_email, full_url, clean_phone_number
from bolibana.web.decorators import provider_permission

logger = logging.getLogger(__name__)


class ProvidersListView(ListView):
    """ Generic List View for Providers """

    context_object_name = 'users_list'
    template_name = 'users_list.html'

    def get_queryset(self):
        return Provider.objects.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super(ProvidersListView, self).get_context_data(**kwargs)
        # Add category
        context['category'] = 'admin'
        context['location'] = 'users'
        return context


class EditProviderForm(forms.Form):

    uid = forms.IntegerField(required=False,
                             widget=forms.widgets.HiddenInput(),
                             label=ugettext_lazy(u"User ID"))
    first_name = forms.CharField(max_length=50, required=True,
                                 label=ugettext_lazy(u"First Name"))
    last_name = forms.CharField(max_length=50, required=True,
                                label=ugettext_lazy(u"Last Name"))
    email = forms.EmailField(required=False,
                             label=ugettext_lazy(u"E-mail Address"))
    phone_number = forms.CharField(max_length=12, required=False,
                                   label=ugettext_lazy(u"Phone Number"))

    phone_number_extra = forms.CharField(max_length=12, required=False,
                                         label=ugettext_lazy(u"Phone Number"))

    role = forms.ChoiceField(label=ugettext_lazy(u"Role"),
                             choices=[(role.slug, role.name)
                                      for role
                                      in Role.objects.all().order_by('name')])

    entity = TreeNodeChoiceField(queryset=Entity.tree.all(),
                                 level_indicator=u'---',
                                 label=ugettext_lazy(u"Entity"))

    def clean_phone_number(self):
        ind, clean_num = clean_phone_number(self.cleaned_data
                                                .get('phone_number'))
        if not ind:
            ind = '223'
        phone_number = '+%s%s' % (ind, clean_num) if clean_num else None
        user_id = self.cleaned_data.get('uid')

        if phone_number \
           and Provider.objects.filter(phone_number=phone_number)\
                               .exclude(id=user_id).count() > 0:
            raise forms.ValidationError(_(u"Phone number already "
                                          u"taken by %(provider)s")
                                        % {'provider': Provider.objects
                                            .get(phone_number=phone_number)
                                            .name_access()})
        return phone_number

    def clean_phone_number_extra(self):
        ind, clean_num = clean_phone_number(self.cleaned_data
                                                .get('phone_number_extra'))
        if not ind:
            ind = '223'
        phone_number = '+%s%s' % (ind, clean_num) if clean_num else None

        return phone_number

    def clean_entity(self):
        if self.cleaned_data.get('role') in ('antim', 'pnlp'):
            return Entity.objects.filter(level=0)[0]
        elif self.cleaned_data.get('role') != 'partners':

            try:
                role = Role.objects.get(slug=self.cleaned_data.get('role'))
            except:
                role = None

            # get level if exist
            level = getattr(role, 'level', None)

            if not level:
                level = self.cleaned_data.get('role')

            if self.cleaned_data.get('entity').type.slug != level:
                raise forms.ValidationError(_(u"Entity is not valid "
                                              u"for this Role."))
        return self.cleaned_data.get('entity')


@provider_permission('can_manage_users')
def add_edit_user(request, user_id=None, template='add_edit_provider.html'):
    context = {'category': 'admin', 'location': 'users'}
    web_provider = request.user.get_profile()

    if request.method == 'POST':

        form = EditProviderForm(request.POST)
        if form.is_valid():
            # build an Access based on Role and Entity selected
            role = Role.objects.get(slug=form.cleaned_data.get('role'))
            # if a national role, force attachment to root entity
            if role.slug in ('antim', 'national'):
                entity = Entity.objects.filter(level=0)[0]
            else:
                entity = form.cleaned_data.get('entity')
            access = Access.find_by(role, entity)

            if user_id:
                provider = Provider.objects.get(id=user_id)
                # remove all access and add new one
                while provider.access.count() > 0 and access != provider.access.all()[0]:
                    provider.access.remove(provider.access.all()[0])
                provider.access.add(access)
            else:
                # forge username
                username = username_from_name(
                    form.cleaned_data.get('first_name'),
                    form.cleaned_data.get('last_name'))

                print username
                # generate password
                password = random_password(username)

                # create Provider
                provider = Provider.create_provider(username,
                                                    'xx', access=[access])
                provider.set_password(password)
            # we have a valid provider whatever the case. update details
            provider.first_name = form.cleaned_data.get('first_name')
            provider.last_name = form.cleaned_data.get('last_name')
            provider.email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            # only update if not None to preserve uniqueness
            if phone_number \
               and Provider.objects.filter(phone_number=phone_number)\
                                   .exclude(id=user_id).count() == 0:
                provider.phone_number = phone_number
            provider.phone_number_extra = \
                form.cleaned_data.get('phone_number_extra')
            provider.save()
            messages.success(request, _(u"Profile details updated."))

            if not user_id and provider.email:
                # send email with password on account creation
                sent, sent_message = send_email(recipients=provider.email,
                                                context={'provider': provider,
                                                         'creator': web_provider,
                                                         'password': password,
                                                         'url': full_url()},
                                                template='emails/new_account.txt',
                                                title_template='emails/title.new_account.txt')
                if sent:
                    messages.success(request, _(u"An e-mail containing the "
                                                "password has been sent "
                                                "to %(email)s")
                                     % {'email': provider.email})
                else:
                    messages.error(request, _(u"Unable to send e-mail "
                                              "to %(email)s. Please record "
                                              "and forward the password: "
                                              "%(pass)s")
                                   % {'email': provider.email,
                                      'pass': password})
                    # log exception
                    logger.warning(u"Unable to send email to %(email)s "
                                   "with Exception %(e)r"
                                   % {'email': provider.email,
                                      'e': sent_message})
            # display password if user has no email address
            elif not user_id and not provider.email:
                messages.info(request, _(u"Please record and forward the "
                                         "generated password: %(pass)s")
                              % {'pass': password})

            return redirect(add_edit_user, provider.id)
        else:
            try:
                provider = Provider.objects.get(id=user_id)
                provider_data = provider.to_dict()
            except Provider.DoesNotExist:
                provider = None
                pass
                #raise Http404
            try:
                provider_data.update({'entity': provider.first_target().id,
                                      'role': provider.first_role().slug})
            except:
                pass
    # GET METHOD
    else:
        if user_id:
            # user_id might be forged and thus innexistant
            try:
                provider = Provider.objects.get(id=user_id)
                provider_data = provider.to_dict()
            except Provider.DoesNotExist:
                raise Http404
            try:
                provider_data.update({'entity': provider.first_target().id,
                                      'role': provider.first_role().slug,
                                      'uid': provider.id})
            except:
                pass
        else:
            provider = {}
            provider_data = {}

        form = EditProviderForm(initial=provider_data)

    context.update({'form': form, 'user_id': user_id, 'provider': provider})

    return render(request, template, context)


@provider_permission('can_manage_users')
def enable_disable_user(request, user_id, activate):
    """ change user's active satus """
    try:
        provider = Provider.objects.get(id=user_id)
    except Provider.DoesNotExist:
        raise Http404(_(u"There is no Provider account with ID #%(id)d")
                      % {'id': int(user_id)})

    if provider.is_active == activate:
        messages.warning(request, _(u"Requested status is same "
                                    "as current user status."))
    else:
        provider.is_active = activate
        provider.save()
        messages.warning(request, _(u"%(provider)s status has been "
                                    "changed to %(status)s")
                         % {'provider': provider.name(),
                            'status': _(u"active")
                            if provider.is_active
                            else _(u"inactive")})
    return redirect('edit_user', provider.id)


@provider_permission('can_manage_users')
def password_user(request, user_id, pwd_id):
    """ Generate new password for user """
    web_provider = request.user.get_profile()

    try:
        provider = Provider.objects.get(id=user_id)
    except Provider.DoesNotExist:
        raise Http404(_(u"There is no Provider account with ID #%(id)d")
                      % {'id': int(user_id)})

    # generate and assign password
    if int(pwd_id) == 0:
        password = random_password()
    else:
        password = random_sample_password()
    provider.set_password(password)
    provider.save()

    if provider.email:
        # send email with password on account creation
        sent, sent_message = send_email(recipients=provider.email,
                                        context={'provider': provider,
                                                 'creator': web_provider,
                                                 'password': password,
                                                 'url': full_url()},
                                        template='emails/new_password.txt',
                                        title_template='emails/title.new_password.txt')
        if sent:
            messages.success(request, _(u"An e-mail containing the "
                                        "password has been sent "
                                        "to %(email)s")
                             % {'email': provider.email})
        else:
            messages.error(request, _(u"Unable to send e-mail "
                                      "to %(email)s. Please record "
                                      "and forward the password: "
                                      "%(pass)s")
                           % {'email': provider.email,
                              'pass': password})
            # log exception
            logger.warning(u"Unable to send email to %(email)s "
                           "with Exception %(e)r"
                           % {'email': provider.email,
                              'e': sent_message})
    # display password if user has no email address
    else:
        messages.info(request, _(u"Please record and forward the "
                                 "generated password: %(pass)s")
                      % {'pass': password})

    return redirect('edit_user', provider.id)
