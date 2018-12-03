from django.contrib.auth.models import User
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import FilterForm
from .models import Filter
from aliases.models import Alias


class FilterTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.aliases = mommy.make(
            Alias,
            user=self.users[0],
            _quantity=2,
            _fill_optional=True
        )
        self.filters = mommy.make(
            Filter,
            user=self.users[0],
            alias=self.aliases[0],
            is_blocked=False,
            _quantity=6,
            _fill_optional=True,
        )
        self.filters[3].user = self.users[1]
        self.filters[3].alias = self.aliases[1]
        self.filters[3].save()
        self.filters[4].user = self.users[1]
        self.filters[4].alias = self.aliases[1]
        self.filters[4].save()
        self.filters[5].user = self.users[1]
        self.filters[5].alias = self.aliases[1]
        self.filters[5].save()

        self.form_data = {
            'name': 'test.test',
        }

    def test_unauthenticated_redirects(self):
        # test all the unauthenticated redirects
        urls = {
            '/filters/{}/create/'.format(self.aliases[0].name): ['post'],
            '/filters/{}/delete/'.format(self.filters[0].pk): ['get', 'post'],
            '/filters/{}/filter/allow/'.format(self.filters[0].pk): ['get'],
            '/filters/{}/filter/block/'.format(self.filters[0].pk): ['get'],
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

    def test_bad_authenticated_404(self):
        # test all the 404 responses for authenticated users
        # who are accessing things they don't have access to
        urls = {
            '/filters/{}/delete/'.format(self.filters[0].pk): ['get', 'post'],
            '/filters/{}/filter/allow/'.format(self.filters[0].pk): ['get'],
            '/filters/{}/filter/block/'.format(self.filters[0].pk): ['get'],
        }

        self.client.force_login(self.users[2])

        for url, method_list in urls.items():
            for method in method_list:
                # check which method to use
                if method == 'post':
                    response = self.client.post(url)
                elif method == 'get':
                    response = self.client.get(url)

            # test for 404
            self.assertEqual(response.status_code, 404)

    def test_filter_exists(self):
        # make sure all of the filters are being created correctly
        filters = Filter.objects.all()
        for filter in self.filters:
            self.assertIn(filter, filters)

    def test_no_filters(self):
        # someone with no created filters should not see any filters
        # login as user 2
        self.client.force_login(self.users[2])

        # view the dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        for filter in self.filters:
            self.assertNotContains(response, filter.name)

    def test_filter_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # submit the POST request
        response = self.client.post('/filters/{}/create/'.format(
            self.aliases[0].name), self.form_data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard shows the new filter
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.form_data['name'])

    def test_filter_form(self):
        # testing the form's validity
        form = FilterForm(self.form_data)
        self.assertEquals(form.is_valid(), True)

    def test_filter_delete(self):
        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # submit the POST request with an empty data dict
        response = self.client.post('/filters/{}/delete/'.format(self.filters[0].pk), {})

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard doesn't show the filter
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.filters[0].name)

        # check that the filter is gone
        filters = Filter.objects.all()
        self.assertNotIn(self.filters[0], filters)

    def test_filter_block(self):
        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # define actions for loop
        actions = ['allow', 'block']

        # test for each action
        for action in actions:

            # GET request for action
            response = self.client.get('/filters/{}/filter/{}/'.format(
                self.filters[0].pk, action))

            # check the redirect
            self.assertRedirects(response,
                '/dashboard/{}/'.format(self.filters[0].alias.name),
                302, 200)

            # reload object's values
            self.filters[0].refresh_from_db()

            # make sure the object has changed
            if action == 'allow':
                self.assertEqual(self.filters[0].is_blocked, False)
            elif action == 'block':
                self.assertEqual(self.filters[0].is_blocked, True)
