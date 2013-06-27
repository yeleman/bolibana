#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.conf import settings

from bolibana.tools.utils import get_level_for, random_proverb


def add_provider(request):
    """ Add the provider object of logged-in user or None """
    try:
        web_provider = request.user
    except:
        web_provider = None

    fortune = random_proverb() if settings.ENABLE_FORTUNE else None
    return {'web_provider': web_provider, 'fortune': fortune}


def add_level(request):
    """ Add level (hierachy slug) of logged-in provider or None """
    try:
        level = get_level_for(request.user)
    except:
        level = None
    return {'level': level}
