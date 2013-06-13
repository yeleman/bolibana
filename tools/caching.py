#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

''' Drop-in caching decorator for functions

    Uses django cache framework to cache the result of any function.

    Usage:
        @cache_result(ident=lambda x, y: 'my_function')
        def heavy_function(x, y):
            # heavy processing
            # network access
            return result

        heavy_function(1, 2, cache=True) '''

from functools import wraps

DEFAULT_CACHE_EXPIRY = 15 * 60  # 15mn
NOT_FOUND = u'#not-found#'


class CacheNotAvailable(object):
    ''' Django cache-compatible class to fake cache code if no django

        Results in no caching at all '''

    def get(self, *args, **kwargs):
        pass

    def get_many(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass

    def set(self, *args, **kwargs):
        pass

    def set_many(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def delete_many(self, *args, **kwargs):
        pass

    def clear(self, *args, **kwargs):
        pass

    def incr(self, *args, **kwargs):
        pass

    def decr(self, *args, **kwargs):
        pass

# import django cache framework
# defaults to a fake interface if django is not available or not configured.
try:
    from django.core.cache import get_cache, InvalidCacheBackendError
except ImportError:
    cache_available = False
else:
    cache_available = True
    cache_stores = {}


def cache_result(ident=None, store='default'):
    ''' cache returned value of function if requested

        decorator takes two arguments:
            * ident
            A string or callable returning the rest of the cache key.
            Usually, you'll want to return the target URL

            * store='default'
            The key of the Django store in CACHES settings.

        decorator allows overloading the target function with cache-specific
        arguments: cache(bool), use_cache(bool),
                   feed_cache(bool) and cache_expiry(int, seconds) '''

    def inner_decorator(target_method):
        def _wrapped_func(*args, **kwargs):

            # sets the cache_store for this call
            if not cache_available:
                cache_store = CacheNotAvailable()
            else:
                # look for the store in Django config
                # add it to the list of available stores and default to NA
                cache_store = cache_stores.get(store, None)
                if cache_store is None:
                    try:
                        cache_store = get_cache(store)
                        cache_stores.update({store: cache_store})
                    except InvalidCacheBackendError:
                        cache_store = CacheNotAvailable()

            def extract_kwargs_cache(**kwargs):
                ''' Analyze cache-related kwargs and seperate them from others

                    use_cache=False
                    Whether to retrieve data from cache (if available)

                    feed_cache=False
                    If data did not came from cache, should we store it?

                    cache_expiry=DEFAULT_CACHE_EXPIRY
                    If storing data to cache, how long should it last?
                    An int representing seconds.

                    cache=True
                    Sets both use_cache and feed_cache to True.
                    Classic caching behavior.

                    Returns: use_cache, feed_cache, expiry, cleaned_kwargs '''
                try:
                    cache = kwargs.pop('cache')
                except KeyError:
                    cache = False
                try:
                    use_cache = kwargs.pop('use_cache')
                except KeyError:
                    use_cache = False
                try:
                    feed_cache = kwargs.pop('feed_cache')
                except KeyError:
                    feed_cache = False

                try:
                    cache_expiry = kwargs.pop('cache_expiry')
                except KeyError:
                    cache_expiry = DEFAULT_CACHE_EXPIRY

                if cache:
                    use_cache = feed_cache = True

                return use_cache, feed_cache, cache_expiry, kwargs

            # analyze cache-related keyword args.
            use_cache, feed_cache, cache_expiry, kwargs = \
                extract_kwargs_cache(**kwargs)

            # if we don't want cache features, shortcut to target data.
            # also skip caching if:
            #   - there's no identifier
            #   - caching is not available/configured
            if (not use_cache and not feed_cache) \
               or not ident \
               or isinstance(cache_store, CacheNotAvailable):

                return target_method(*args, **kwargs)

            # the cache key is compose of a prefix and an ident string
            # in most cases, the prefix would be the HTTP method (GET, POST,..)
            # and the ident string would be an URL
            if callable(ident):
                cache_key = ident(*args, **kwargs)
            else:
                cache_key = ident
            value = NOT_FOUND

            # try to get the data from the cache
            if use_cache:
                # fetch data from cache, defaulting to NOT_FOUND
                value = cache_store.get(cache_key, NOT_FOUND)

            # if the cache retrieved data, return it
            if value != NOT_FOUND:
                return value

            # now, we need we need to fetch the data.
            # let's call the target code
            value = target_method(*args, **kwargs)

            if feed_cache:
                cache_store.set(cache_key, value, cache_expiry)

            return value
        return wraps(target_method)(_wrapped_func)
    return inner_decorator
