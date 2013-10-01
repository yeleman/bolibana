#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import unicodedata
import random
import re

from django.contrib.auth import get_user_model

PASSWORD_LENGTH = 8
PASSWORD_LENGTH_SAMPLE = 4
USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 8


def random_password():
    """ random password suitable for mobile typing """
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
                    for i in range(PASSWORD_LENGTH)])


def random_sample_password():
    """ random sample password suitable for mobile typing """
    num_chars = PASSWORD_LENGTH_SAMPLE
    letters = 'abcdefghijklmnopqrstuvwxyz'
    index = random.randint(0, len(letters) - 1)

    password = letters[index]
    num_chars -= 1
    while num_chars:
        num_chars -= 1
        index += 1
        try:
            password += letters[index]
        except IndexError:
            password += letters[index - 26]
    postfix = random.randint(0, 9)
    password += str(postfix)
    return(password)


def username_from_name(first_name, last_name):
    """ available username to use on get_user_model() forged from first and last name """

    def new_slug(text, salt=None):
        """ assemble text and salt providing optimum length """
        if salt:
            username = text[:(USERNAME_MAX_LENGTH - salt.__len__())] + salt
        else:
            username = text[:USERNAME_MAX_LENGTH]
        if username.__len__() < USERNAME_MIN_LENGTH:
            username = "{0:{1}<{2}}".format(username, "a", USERNAME_MIN_LENGTH)
        return username

    def is_available(username):
        """ DB check for username use """
        return get_user_model().objects.filter(username=username).count() == 0

    def jdoe(first, last):
        """ first name initial followed by last name format """
        return "{}{}".format(first[0], last)

    def johndoe(first, last):
        """ first name followed by last name format """
        return "{}{}".format(first, last)

    def iterate(username):
        """ adds and increment a counter at end of username """
        # make sure username matches length requirements
        username = new_slug(username)
        if not is_available(username):
            # find the counter if any
            sp = re.split(r'([0-9]+)$', username)
            if sp.__len__() == 3:
                # increment existing counter
                username = sp[0]
                salt = str(int(sp[1]) + 1)
            else:
                # start counter at 1
                salt = '1'
            # bundle counter and username then loop
            return iterate(new_slug(username, salt))
        else:
            # username is available
            return username

    def string_to_slug(s):
        raw_data = s
        try:
            raw_data = unicodedata.normalize('NFKD',
                                             raw_data.decode('utf-8',
                                                             'replace'))\
                                  .encode('ascii', 'ignore')
        except:
            pass
        return re.sub(r'[^a-z0-9-]+', '', raw_data.lower()).strip()

    # normalize first and last name to ASCII only
    first_name = string_to_slug(first_name.lower())
    last_name = string_to_slug(last_name.lower())

    # iterate over a jdoe format
    return iterate(jdoe(first_name, last_name))
