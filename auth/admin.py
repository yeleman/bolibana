#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.contrib import admin


class RoleAdmin(admin.ModelAdmin):

    pass


class PermissionAdmin(admin.ModelAdmin):

    pass


class AccessAdmin(admin.ModelAdmin):

    pass


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'first_access', \
                    'phone_number', 'email', 'is_active', 'is_staff')
    search_fields = ['username', 'first_name', 'last_name', 'email']
