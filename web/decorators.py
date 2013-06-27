#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from bolibana.web.http import Http403
from bolibana.tools.utils import provider_can_or_403


def provider_required(target):
    """ Web view decorator ensuring visitor is a logged-in Provider """
    def wrapper(request, *args, **kwargs):
        try:
            web_provider = request.user
        except:
            # either not logged-in or non-provider user
            web_provider = None
        if not web_provider.is_anonymous() and web_provider.is_active:
            # user is a provider, forward to view
            return target(request, *args, **kwargs)
        else:
            # if user is logged-in (non-provider)
            # send him a message
            if request.user.is_authenticated():
                messages.error(request, _("The credentials you are "
                                          "using to log in are not "
                                          "valid. Please contact ANTIM."))
            # then foward logged-in or not to the login page.
            # logged-in users will see message there.
            return redirect('/login')
    return wrapper


def provider_permission(permission, entity=None):
    """ Web views decorator checking for premission on entity """
    def decorator(target):
        def wrapper(request, *args, **kwargs):
            try:
                web_provider = request.user
                assert(web_provider)
                assert(web_provider.is_active)
                assert(not web_provider.is_anonymous())
            except:
                # user is not a provider. could be logged-in though.
                # forwards to provider_required
                return provider_required(target)(request, *args, **kwargs)
            else:
                # user is valid provider.
                # need to check if has permission. if not, 403.
                if provider_can_or_403(permission, web_provider, entity):
                    return target(request, *args, **kwargs)
                raise Http403
        return wrapper
    return decorator
