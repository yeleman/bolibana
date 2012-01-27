#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _, ugettext

from bolibana.tools.utils import generate_user_hash


class ActiveManager(models.Manager):

    def get_query_set(self):
        return super(ActiveManager, self).get_query_set() \
                        .filter(user__is_active=True)


class Provider(models.Model):

    """ A User Profile for django.auth

        Django User on `.user`
        All User methods and prop. proxied for easy access in templates """

    class Meta:
        app_label = 'bolibana'
        verbose_name = _(u"Provider")
        verbose_name_plural = _(u"Providers")

    user = models.OneToOneField(User, unique=True, verbose_name=_(u"User"))

    phone_number = models.CharField(max_length=12, unique=True, \
                                    null=True, blank=True, \
                                    verbose_name=_(u"Phone Number"))
    phone_number_extra = models.CharField(max_length=12, \
                                    null=True, blank=True, \
                                    verbose_name=_(u"Phone Number"))
    access = models.ManyToManyField('Access', null=True, blank=True, \
                                    verbose_name=_(u"Access"))
    pwhash = models.CharField(max_length=255, \
                                    null=True, blank=True, \
                                    verbose_name=_(u"Password Hash"))

    # django manager first
    objects = models.Manager()
    active = ActiveManager()

    def __unicode__(self):
        return self.name()

    def name(self):
        """ prefered representation of the provider's name """
        if self.first_name and self.last_name:
            return u"%(first)s %(last)s" % {'first': self.first_name.title(), \
                                            'last': self.last_name.title()}
        if self.first_name:
            return self.first_name.title()

        if self.last_name:
            return self.last_name.title()

        return self.username

    def name_access(self):
        access = self.first_access()
        if access:
            return ugettext(u"%(name)s (%(access)s)") \
                   % {'name': self.name(), \
                      'access': access.name()}
        else:
            return self.name()

    def to_dict(self):
        return {'first_name': self.first_name, 'last_name': self.last_name, \
                'username': self.username, 'phone_number': self.phone_number, \
                'email': self.email, \
                'phone_number_extra': self.phone_number_extra}

    @classmethod
    def create_provider(cls, username, password, \
                        phone_number=None, access=None):
        """ shortcut creation of provider with its associated User """
        user, created = User.objects.get_or_create(username=username, \
                                                   password=password)
        user.save()
        provider = user.get_profile()
        provider.phone_number = phone_number
        provider.pwhash = cls.generate_hash(username, password)
        if access:
            for indiv_access in access:
                provider.access.add(indiv_access)
        provider.save()
        return provider

    def has_permission(self, perm_slug, entity=None):
        """ whether or not User has this permission for Enitity """
        qs = self.access.all()
        if entity != None:
            qs = qs.filter(target=entity)
        for access in qs:
            if perm_slug in [p.slug for p in access.role.permissions.all()]:
                return True
        return False

    def first_role(self):
        """ only or main role if Provider has many """
        try:
            return self.first_access().role
        except AttributeError:
            return None

    def first_access(self):
        """ only or main access if Provider has many """
        try:
            return self.access.all()[0]
        except IndexError:
            return None

    def first_target(self):
        try:
            return self.first_access().target
        except AttributeError:
            return None

    def check_hash(self, pwhash):
        return self.pwhash == pwhash

    @classmethod
    def generate_hash(cls, username, password):
        return generate_user_hash(username, password)

    # following accessors and methods are proxies to
    # the user's one.
    # allows easy replacement of Provider by User

    def get_username(self):
        return self.user.username

    def set_username(self, value):
        self.user.username = value
    username = property(get_username, set_username)

    def get_first_name(self):
        return self.user.first_name

    def set_first_name(self, value):
        self.user.first_name = value
    first_name = property(get_first_name, set_first_name)

    def get_last_name(self):
        return self.user.last_name

    def set_last_name(self, value):
        self.user.last_name = value
    last_name = property(get_last_name, set_last_name)

    def get_email(self):
        return self.user.email

    def set_email(self, value):
        self.user.email = value
    email = property(get_email, set_email)

    def get_is_staff(self):
        return self.user.is_staff

    def set_is_staff(self, value):
        self.user.is_staff = value
    is_staff = property(get_is_staff, set_is_staff)

    def get_is_active(self):
        return self.user.is_active

    def set_is_active(self, value):
        self.user.is_active = value
    is_active = property(get_is_active, set_is_active)

    def get_is_superuser(self):
        return self.user.is_superuser

    def set_is_superuser(self, value):
        self.user.is_superuser = value
    is_superuser = property(get_is_superuser, set_is_superuser)

    def get_last_login(self):
        return self.user.last_login

    def set_last_login(self, value):
        self.user.last_login = value
    last_login = property(get_last_login, set_last_login)

    def get_date_joined(self):
        return self.user.date_joined

    def set_date_joined(self, value):
        self.user.date_joined = value
    date_joined = property(get_date_joined, set_date_joined)

    def is_anonymous(self):
        return self.user.is_anonymous()

    def is_authenticated(self):
        return self.user.is_authenticated()

    # this one is not a proxy
    def get_full_name(self):
        return self.name()

    def set_password(self, raw_password):
        self.pwhash = self.generate_hash(self.username, raw_password)
        self.save()
        return self.user.set_password(raw_password)

    def check_password(self, raw_password):
        return self.user.check_password(raw_password)

    def set_unusable_password(self):
        return self.user.set_unusable_password()

    def has_usable_password(self):
        return self.user.has_usable_password()

    def get_group_permissions(self, obj=None):
        return self.user.get_group_permissions(obj)

    def get_all_permissions(self, obj=None):
        return self.user.get_all_permissions(obj)

    def has_perm(self, perm, obj=None):
        return self.user.has_perm(perm, obj)

    def has_perms(self, perm_list, obj=None):
        return self.user.has_perms(perm_list, obj)

    def has_module_perms(self, package_name):
        return self.user.has_module_perms(package_name)

    def email_user(self, subject, message, from_email=None):
        return self.user.email_user(subject, message, from_email)

    def get_profile(self):
        return self


def save_associated_user(sender, instance, created, **kwargs):
    if not created:
        instance.user.save()


def create_user_provider(sender, instance, created, **kwargs):
    if created:
        provider, created = Provider.objects.get_or_create(user=instance)

post_save.connect(create_user_provider, sender=User)
post_save.connect(save_associated_user, sender=Provider)
