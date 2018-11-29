from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import AliasForm
from .models import Alias, ForwardingEmail


class AliasTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.aliases = mommy.make(
            Alias,
            user=self.users[0],
            _quantity=5,
            _fill_optional=True,
        )
        self.aliases[3].user = self.users[1]
        self.aliases[3].save()
        self.aliases[4].user = self.users[1]
        self.aliases[4].save()

    def test_alias_exists(self):
        # make sure all of the aliases are being created correctly
        aliases = Alias.objects.all()
        for alias in self.aliases:
            self.assertIn(alias, aliases)

    def test_unique_alias(self):
        # aliases must be unique, so make sure this throws an error
        # when trying to create an alias with a name that already exists
        with self.assertRaises(IntegrityError):
            alias = mommy.make(Alias, name=self.aliases[0].name)

    def test_alias_unauthenticated_redirects(self):
        # test all the unauthenticated redirects here
        # so we don't have to do them individually in all the other tests
        urls = {
            '/aliases/create/': 'post',
        }

        for url, method in urls.items():
            # check which method to use
            if method == 'post':
                response = self.client.post(url)
            elif method == 'get':
                response = self.client.get(url)

            # test for the redirect
            self.assertRedirects(response, '/accounts/login/?next={}'.format(url), 302, 200)

    def test_alias_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # set the POST data
        alias_name = "testalias"
        data = {
            'name': alias_name,
        }

        # submit the POST data
        response = self.client.post('/aliases/create/', data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response, '/dashboard/', 302, 200)

        # check that the dashboard shows the new alias name
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, alias_name)

    def test_alias_form(self):
        # testing the form's validity
        form = AliasForm({
            'name': 'testalias',
        })
        self.assertEquals(form.is_valid(), True)

class ForwardingEmailTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.forwardingemails = mommy.make(
            ForwardingEmail,
            user=self.users[0],
            _quantity=5,
            _fill_optional=True,
        )
        self.forwardingemails[2].user = self.users[1]
        self.forwardingemails[2].save()
        self.forwardingemails[3].user = self.users[1]
        self.forwardingemails[3].save()
        self.forwardingemails[4].user = self.users[1]
        self.forwardingemails[4].save()

    def test_forwardingemail_exists(self):
        # make sure all of the forwardingemails are being created correctly
        forwardingemails = ForwardingEmail.objects.all()
        for forwardingemail in self.forwardingemails:
            self.assertIn(forwardingemail, forwardingemails)
