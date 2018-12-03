from django.contrib.auth.models import User
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from aliases.models import Alias
from filters.models import Filter
from recipients.models import Recipient


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

        self.recipients = mommy.make(
            Recipient,
            user=self.users[0],
            _quantity=5,
            _fill_optional=True,
        )
        self.recipients[2].user = self.users[1]
        self.recipients[2].save()
        self.recipients[3].user = self.users[1]
        self.recipients[3].save()
        self.recipients[4].user = self.users[1]
        self.recipients[4].save()

        self.filters = mommy.make(
            Filter,
            user=self.users[0],
            _quantity=6,
            _fill_optional=True,
        )
        self.filters[3].user = self.users[1]
        self.filters[3].save()
        self.filters[4].user = self.users[1]
        self.filters[4].save()
        self.filters[5].user = self.users[1]
        self.filters[5].save()

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

                    # check for user's recipients
                    for recipient in self.recipients:
                        if recipient.user == user and recipient.alias == alias:
                            self.assertContains(response, recipient.email)
                        else:
                            self.assertNotContains(response, recipient.email)

                    # check for user's filters
                    for filter in self.filters:
                        if filter.user == user and filter.alias == alias:
                            self.assertContains(response, filter.name)
                        else:
                            self.assertNotContains(response, filter.name)

                else:
                    self.assertNotContains(response, alias.name)

            self.client.logout()
