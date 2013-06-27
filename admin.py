#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms

from bolibana.models.Provider import Provider


class EntityAdmin(admin.ModelAdmin):

    list_display = ('slug', 'name', 'type', 'parent', 'parent_level')
    list_filter = ('type', 'parent')
    ordering = ('slug',)
    search_fields = ('slug', 'name')


class EntityTypeAdmin(admin.ModelAdmin):

    pass


class PeriodAdmin(admin.ModelAdmin):

    pass


class MonthPeriodAdmin(admin.ModelAdmin):

    pass


class YearPeriodAdmin(admin.ModelAdmin):

    pass


class ReportAdmin(admin.ModelAdmin):

    pass


class RoleAdmin(admin.ModelAdmin):

    pass


class PermissionAdmin(admin.ModelAdmin):

    pass


class AccessAdmin(admin.ModelAdmin):

    pass


def get_fieldsets(cls, attr):
    fs = []
    for item in getattr(cls, attr):
        fs.append(item)
    fs.append((None, {'fields': ('access', 'phone_number', 'phone_number_extra')}))
    return tuple(fs)


class ProviderModificationForm(UserChangeForm):
    class Meta:
        model = Provider


class ProviderCreationForm(forms.ModelForm):
    class Meta:
        model = Provider
        field = ('username', )

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ProviderCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProviderAdmin(UserAdmin):
    form = ProviderModificationForm
    add_form = ProviderCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'first_name', 'last_name',
                       'is_superuser', 'is_staff', 'is_active',
                       'access', 'phone_number', 'phone_number_extra')}),
    )
    fieldsets = get_fieldsets(UserAdmin, 'fieldsets')
