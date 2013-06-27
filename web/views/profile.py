#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _, ugettext_lazy

from bolibana.web.decorators import provider_required


class ProviderForm(forms.Form):

    first_name = forms.CharField(max_length=50, required=False,
                                 label=ugettext_lazy("First Name"))
    last_name = forms.CharField(max_length=50, required=False,
                                label=ugettext_lazy("Last Name"))
    email = forms.EmailField(required=False,
                             label=ugettext_lazy("E-mail Address"))
    phone_number = forms.CharField(max_length=12, required=False,
                                   label=ugettext_lazy("Phone Number"))
    phone_number_extra = forms.CharField(max_length=12, required=False,
                                         label=ugettext_lazy("Phone Number"))


class ProviderPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=100,
                                label=ugettext_lazy("New Password"),
                                widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(max_length=100,
                                label=ugettext_lazy("Confirm New Password"),
                                widget=forms.PasswordInput(render_value=False))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError(_("You must confirm your password"))
        if password1 != password2:
            raise forms.ValidationError(_("Your passwords do not match"))
        return password2


@provider_required
def edit_profile(request, template='edit_profile.html'):
    context = {}
    provider = request.user

    is_password = 'password1' in request.POST

    if request.method == 'POST' and not is_password:
        form = ProviderForm(request.POST)
        if form.is_valid() and not is_password:
            provider.first_name = form.cleaned_data.get('first_name')
            provider.last_name = form.cleaned_data.get('last_name')
            provider.email = form.cleaned_data.get('email')
            provider.phone_number = form.cleaned_data.get('phone_number')
            provider.phone_number_extra = \
                form.cleaned_data.get('phone_number_extra')
            provider.save()
            messages.success(request, _("Profile details updated."))
            return redirect('index')
    elif is_password:
        form = ProviderForm(provider.to_dict())

    if request.method == 'POST' and is_password:
        passwd_form = ProviderPasswordForm(request.POST)
        if passwd_form.is_valid() and is_password:
            provider.set_password(passwd_form.cleaned_data.get('password1'))
            provider.save()
            messages.success(request, _("Password updated."))
            return redirect('logout')
    elif not is_password:
        passwd_form = ProviderPasswordForm()

    if request.method == 'GET':
        form = ProviderForm(provider.to_dict())
        passwd_form = ProviderPasswordForm()

    context.update({'form': form, 'passwd_form': passwd_form,
                    'provider': provider})

    return render(request, template, context)
