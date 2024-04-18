from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


ASTRONOMY_URL = reverse("planetarium:astronomyshow-list")


class UnAuthenticatedAstronomyShowTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_astronomy_show(self):
        res = self.client.get(ASTRONOMY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
