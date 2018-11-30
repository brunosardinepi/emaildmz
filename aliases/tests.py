from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import AliasForm
from .models import Alias


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

    def test_unauthenticated_redirects(self):
        # test all the unauthenticated redirects here
        # so we don't have to do them individually in all the other tests
        urls = {
            '/aliases/create/': ['post'],
            '/aliases/delete/{}/'.format(self.aliases[0].name): ['get', 'post'],
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
