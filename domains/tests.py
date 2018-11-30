from django.contrib.auth.models import User
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import DomainForm
from .models import Domain
from aliases.models import Alias


class DomainTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.aliases = mommy.make(
            Alias,
            user=self.users[0],
            _quantity=2,
            _fill_optional=True
        )
        self.domains = mommy.make(
            Domain,
            user=self.users[0],
            alias=self.aliases[0],
            is_blocked=False,
            _quantity=6,
            _fill_optional=True,
        )
        self.domains[3].user = self.users[1]
        self.domains[3].alias = self.aliases[1]
        self.domains[3].save()
        self.domains[4].user = self.users[1]
        self.domains[4].alias = self.aliases[1]
        self.domains[4].save()
        self.domains[5].user = self.users[1]
        self.domains[5].alias = self.aliases[1]
        self.domains[5].save()

        self.form_data = {
            'name': 'test.test',
        }

    def test_unauthenticated_redirects(self):
        # test all the unauthenticated redirects
        urls = {
            '/domains/{}/create/'.format(self.aliases[0].name): ['post'],
            '/domains/{}/delete/'.format(self.domains[0].pk): ['get', 'post'],
            '/domains/{}/filter/allow/'.format(self.domains[0].pk): ['get'],
            '/domains/{}/filter/block/'.format(self.domains[0].pk): ['get'],
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
            '/domains/{}/delete/'.format(self.domains[0].pk): ['get', 'post'],
            '/domains/{}/filter/allow/'.format(self.domains[0].pk): ['get'],
            '/domains/{}/filter/block/'.format(self.domains[0].pk): ['get'],
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

    def test_domain_exists(self):
        # make sure all of the domains are being created correctly
        domains = Domain.objects.all()
        for domain in self.domains:
            self.assertIn(domain, domains)

    def test_no_domains(self):
        # someone with no created domains should not see any domains
        # login as user 2
        self.client.force_login(self.users[2])

        # view the dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        for domain in self.domains:
            self.assertNotContains(response, domain.name)

    def test_domain_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # submit the POST request
        response = self.client.post('/domains/{}/create/'.format(
            self.aliases[0].name), self.form_data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard shows the new domain
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.form_data['name'])

    def test_domain_form(self):
        # testing the form's validity
        form = DomainForm(self.form_data)
        self.assertEquals(form.is_valid(), True)

    def test_domain_delete(self):
        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # submit the POST request with an empty data dict
        response = self.client.post('/domains/{}/delete/'.format(self.domains[0].pk), {})

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard doesn't show the domain
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.domains[0].name)

        # check that the domain is gone
        domains = Domain.objects.all()
        self.assertNotIn(self.domains[0], domains)

    def test_domain_block(self):
        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # define actions for loop
        actions = ['allow', 'block']

        # test for each action
        for action in actions:

            # GET request for action
            response = self.client.get('/domains/{}/filter/{}/'.format(
                self.domains[0].pk, action))

            # check the redirect
            self.assertRedirects(response,
                '/dashboard/{}/'.format(self.domains[0].alias.name),
                302, 200)

            # reload object's values
            self.domains[0].refresh_from_db()

            # make sure the object has changed
            if action == 'allow':
                self.assertEqual(self.domains[0].is_blocked, False)
            elif action == 'block':
                self.assertEqual(self.domains[0].is_blocked, True)
