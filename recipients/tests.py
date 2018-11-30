from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .forms import RecipientForm
from .models import Recipient
from aliases.models import Alias


class RecipientTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

        self.aliases = mommy.make(
            Alias,
            user=self.users[0],
            _quantity=2,
            _fill_optional=True
        )
        self.aliases[1].user = self.users[1]
        self.aliases[1].save()

        self.recipients = mommy.make(
            Recipient,
            user=self.users[0],
            alias=self.aliases[0],
            _quantity=5,
            _fill_optional=True,
        )
        self.recipients[2].user = self.users[1]
        self.recipients[2].alias = self.aliases[1]
        self.recipients[2].save()
        self.recipients[3].user = self.users[1]
        self.recipients[3].alias = self.aliases[1]
        self.recipients[3].save()
        self.recipients[4].user = self.users[1]
        self.recipients[4].alias = self.aliases[1]
        self.recipients[4].save()

        self.form_data = {
            'email': 'test@test.test',
        }

    def test_unauthenticated_redirects(self):
        # test all the unauthenticated redirects here
        # so we don't have to do them individually in all the other tests
        urls = {
            '/recipients/{}/create/'.format(self.aliases[0].name): ['post'],
            '/recipients/{}/delete/'.format(self.recipients[0].pk): ['get', 'post'],
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

    def test_recipient_exists(self):
        # make sure all of the recipients are being created correctly
        recipients = Recipient.objects.all()
        for recipient in self.recipients:
            self.assertIn(recipient, recipients)

    def test_no_recipients(self):
        # someone with no created recipients should not see any recipients
        # login as user 2
        self.client.force_login(self.users[2])

        # view the dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        for recipient in self.recipients:
            self.assertNotContains(response, recipient.email)

    def test_recipient_create(self):
        # login as user 0
        self.client.force_login(self.users[0])

        # submit the POST request
        response = self.client.post('/recipients/{}/create/'.format(
            self.aliases[0].name), self.form_data)

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard shows the new recipient
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.form_data['email'])

    def test_recipient_form(self):
        # testing the form's validity
        form = RecipientForm(self.form_data)
        self.assertEquals(form.is_valid(), True)

    def test_recipient_delete(self):
        # login as user 1 (not the owner)
        self.client.force_login(self.users[1])

        # submit the POST request with an empty data dict
        response = self.client.post('/recipients/{}/delete/'.format(
            self.recipients[0].pk), {})

        # make sure it raises 404
        self.assertEqual(response.status_code, 404)

        # logout as user 1
        self.client.logout()

        # login as user 0 (owner)
        self.client.force_login(self.users[0])

        # submit the POST request with an empty data dict
        response = self.client.post('/recipients/{}/delete/'.format(
            self.recipients[0].pk), {})

        # make sure it redirects to the dashboard
        self.assertRedirects(response,
            '/dashboard/{}/'.format(self.aliases[0].name),
            302, 200)

        # check that the dashboard doesn't show the recipient
        response = self.client.get('/dashboard/{}/'.format(self.aliases[0].name))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.recipients[0].email)

        # check that the recipient is gone
        recipients = Recipient.objects.all()
        self.assertNotIn(self.recipients[0], recipients)

