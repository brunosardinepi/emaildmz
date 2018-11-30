from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import AliasForm, ForwardingEmailForm
from .models import Alias, ForwardingEmail


class UnauthenticedRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = mommy.make(User)

        self.alias = mommy.make(
            Alias,
            user=self.user,
            _fill_optional=True,
        )

        self.forwardingemail = mommy.make(
            ForwardingEmail,
            user=self.user,
            alias=self.alias,
            _fill_optional=True,
        )

    def test_unauthenticated_redirects(self):
        # test all the unauthenticated redirects here
        # so we don't have to do them individually in all the other tests
        urls = {
            '/aliases/create/': ['post'],
            '/aliases/delete/{}/'.format(self.alias.name): ['get', 'post'],
            '/aliases/{}/forwardingemail/create/'.format(self.alias.name): ['post'],
            '/aliases/forwardingemail/{}/delete/'.format(
                self.forwardingemail.pk): ['get', 'post'],
        }

        for url, method_list in urls.items():
            for method in method_list:
                # check which method to use
                if method == 'post':
                    response = self.client.post(url)
                elif method == 'get':
                    response = self.client.get(url)

            # test for the redirect
            self.assertRedirects(response, '/accounts/login/?next={}'.format(url), 302, 200)

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

        self.form_data = {
            'name': 'testalias',
        }

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

    def test_no_aliases(self):
        # someone with no created aliases should not see any aliases
        # login as user 2
        self.client.force_login(self.users[2])

        # view the dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        for alias in self.aliases:
            self.assertNotContains(response, alias.name)

    def test_alias_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # submit the POST request
        response = self.client.post('/aliases/create/', self.form_data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.form_data['name']),
            302, 200)

        # check that the dashboard shows the new alias name
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.form_data['name'])

    def test_alias_form(self):
        # testing the form's validity
        form = AliasForm(self.form_data)
        self.assertEquals(form.is_valid(), True)

    def test_alias_delete(self):
        # login as user 1 (not the owner)
        self.client.force_login(self.users[1])

        # submit the POST request with an empty data dict
        response = self.client.post('/aliases/delete/{}/'.format(
            self.aliases[0].name), {})

        # make sure it raises 404
        self.assertEqual(response.status_code, 404)

        # logout as user 1
        self.client.logout()

        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # submit the POST request with an empty data dict
        response = self.client.post('/aliases/delete/{}/'.format(
            self.aliases[0].name), {})

        # make sure it redirects to the dashboard
        self.assertRedirects(response, '/dashboard/', 302, 200)

        # check that the dashboard doesn't show the name
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.aliases[0].name)

        # check that the alias is gone
        aliases = Alias.objects.all()
        self.assertNotIn(self.aliases[0], aliases)

class ForwardingEmailTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.alias = mommy.make(
            Alias,
            user=self.users[0],
            _fill_optional=True
        )

        self.forwardingemails = mommy.make(
            ForwardingEmail,
            user=self.users[0],
            alias=self.alias,
            _quantity=5,
            _fill_optional=True,
        )
        self.forwardingemails[2].user = self.users[1]
        self.forwardingemails[2].save()
        self.forwardingemails[3].user = self.users[1]
        self.forwardingemails[3].save()
        self.forwardingemails[4].user = self.users[1]
        self.forwardingemails[4].save()

        self.form_data = {
            'email': 'test@test.test',
        }

    def test_forwardingemail_exists(self):
        # make sure all of the forwardingemails are being created correctly
        forwardingemails = ForwardingEmail.objects.all()
        for forwardingemail in self.forwardingemails:
            self.assertIn(forwardingemail, forwardingemails)

    def test_no_forwardingemails(self):
        # someone with no created forwardingemails should not see any forwardingemails
        # login as user 2
        self.client.force_login(self.users[2])

        # view the dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        for forwardingemail in self.forwardingemails:
            self.assertNotContains(response, forwardingemail.email)

    def test_forwardingemail_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # submit the POST request
        response = self.client.post('/aliases/{}/forwardingemail/create/'.format(
            self.alias.name), self.form_data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.alias.name),
            302, 200)

        # check that the dashboard shows the new forwardingemail
        response = self.client.get('/dashboard/{}/'.format(self.alias.name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.form_data['email'])

    def test_forwardingemail_form(self):
        # testing the form's validity
        form = ForwardingEmailForm(self.form_data)
        self.assertEquals(form.is_valid(), True)

    def test_forwardingemail_delete(self):
        # login as user 1 (not the owner)
        self.client.force_login(self.users[1])

        # submit the POST request with an empty data dict
        response = self.client.post('/aliases/forwardingemail/{}/delete/'.format(
            self.forwardingemails[0].pk), {})

        # make sure it raises 404
        self.assertEqual(response.status_code, 404)

        # logout as user 1
        self.client.logout()

        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # submit the POST request with an empty data dict
        response = self.client.post('/aliases/forwardingemail/{}/delete/'.format(
            self.forwardingemails[0].pk), {})

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.alias.name),
            302, 200)

        # check that the dashboard doesn't show the forwardingemail
        response = self.client.get('/dashboard/{}/'.format(self.alias.name))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.forwardingemails[0].email)

        # check that the forwardingemail is gone
        forwardingemails = ForwardingEmail.objects.all()
        self.assertNotIn(self.forwardingemails[0], forwardingemails)

