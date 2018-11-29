from django.contrib.auth.models import User
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from aliases.models import Alias, ForwardingEmail
from domains.models import Domain


class HomeTest(TestCase):
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

        self.domains = mommy.make(
            Domain,
            user=self.users[0],
            _quantity=6,
            _fill_optional=True,
        )
        self.domains[3].user = self.users[1]
        self.domains[3].save()
        self.domains[4].user = self.users[1]
        self.domains[4].save()
        self.domains[5].user = self.users[1]
        self.domains[5].save()

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/', 302, 200)

        for user in self.users:
            self.client.force_login(user)
            response = self.client.get('/dashboard/')

            self.assertEqual(response.status_code, 200)

            # check for user's aliases
            for alias in self.aliases:
                if alias.user == user:
                    self.assertContains(response, alias.name)
                else:
                    self.assertNotContains(response, alias.name)

            # check for user's forwardingemails
            for forwardingemail in self.forwardingemails:
                if forwardingemail.user == user:
                    self.assertContains(response, forwardingemail.email)
                else:
                    self.assertNotContains(response, forwardingemail.email)

            # check for user's domains
            for domain in self.domains:
                if domain.user == user:
                    self.assertContains(response, domain.name)
                else:
                    self.assertNotContains(response, domain.name)

            self.client.logout()
