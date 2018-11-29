from django.contrib.auth.models import User
from django.test import Client, TestCase

import unittest

from model_mommy import mommy

from . import views
from .models import Domain


class DomainTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.users = mommy.make(User, _quantity=3)

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

    def test_domain_exists(self):
        domains = Domain.objects.all()
        for domain in self.domains:
            self.assertIn(domain, domains)
