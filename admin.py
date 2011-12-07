#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.contrib import admin


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


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'first_access',
                    'phone_number', 'phone_number_extra', 'email',
                    'is_active', 'is_staff')
    search_fields = ['username', 'first_name', 'last_name', 'email']
