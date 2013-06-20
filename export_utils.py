#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import csv
import codecs
import cStringIO

from bolibana.models import Provider, MonthPeriod, Entity, Report


class DictDiffer(object):
    """ Calculate the difference between two dictionaries """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_new_code_from_csv(old_code, filename):
    with open(filename) as f:
        for line in f.readlines():
            old, new = line.split(',', 1)
            if old == old_code:
                return new
    raise ValueError("Unable to find new code for %s" % old_code)


def period_to(period, as_class=None):
    return {'class': str(period.__class__) if as_class is None else as_class,
            'middle': datetime_to(period.middle())}


def role_to(role):
    return role.slug  # temporary shortcut
    return get_new_code_from_csv(role.slug, 'old_new_roles_pnlp.csv')


def entity_to(entity):

    return entity.slug  # temporary shortcut
    return get_new_code_from_csv(entity.slug, 'old_new_codes_pnlp.csv')


def get_username_from(user_id):
    if user_id is None:
        return None
    if isinstance(user_id, Provider):
        return user_id.username
    return Provider.objects.get(id=user_id).username


def get_period_from(period_id, version):
    try:
        return period_to(MonthPeriod.objects.get(id=period_id))
    except MonthPeriod.DoesNotExist:
        month, year = version.object_repr.split('/', 1)[-1].split()
        return period_to(MonthPeriod.find_create_from(year=int(year),
                                                      month=int(month)))


def get_entity_for(entity_id):
    if isinstance(entity_id, Entity):
        return entity_to(entity_id)
    return entity_to(Entity.objects.get(id=entity_id))


def datetime_to(date_obj):
    return date_obj.isoformat()


def status_to(status):
    return Report.STATUSES_STR.get(status)


def type_to(_type):
    return Report.TYPES_STR.get(_type)


def serialize_provider(provider):

    data = {}
    # static fields
    for field in ('username', 'first_name', 'last_name', 'email',
                  'is_staff', 'is_active', 'is_superuser', 'last_login',
                  'date_joined', 'phone_number', 'phone_number_extra',
                  'pwhash'):
        data.update({field: getattr(provider, field)})

    # format dates
    data.update({'date_joined': datetime_to(data.get('date_joined')),
                 'last_login': datetime_to(data.get('last_login'))})

    # password only in dj User
    data.update({'password': provider.user.password})

    # access and role. we used only one so far
    data.update({'role': role_to(provider.first_role()),
                 'entity': entity_to(provider.first_target())})

    return data
