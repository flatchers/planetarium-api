from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from product.models import PlanetariumDome
from product.serializers import PlanetariumDomeSerializer


PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


def planetarium_dome_url(dome_id):
    return reverse("planetarium:planetariumdome-detail", args=(dome_id,))


def sample_planetarium_dome(**params):
    default = {
        "name": "Unimaginable",
        "rows": 20,
        "seats_in_row": 30
    }
    default.update(params)
    return PlanetariumDome.objects.create(**default)


class UnAuthenticatedPlanetariumDomeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlanetariumDomeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="Test1",
            email="user@admin.test",
            password="123465"
        )
        self.client.force_authenticate(self.user)

    def test_planetarium_dome_list(self):
        sample_planetarium_dome()
        res = self.client.get(PLANETARIUM_DOME_URL)
        planetarium_dome = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeSerializer(planetarium_dome, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_planetarium_dome_retrieve(self):
        info = sample_planetarium_dome()
        url = self.client.get(planetarium_dome_url(info.id))
        serializer = PlanetariumDomeSerializer(info)
        self.assertEqual(url.status_code, status.HTTP_200_OK)
        self.assertEqual(url.data, serializer.data)

    def test_planetarium_dome_post_forbidden(self):
        payload = {
            "name": "forbidden",
        }
        res = self.client.post(PLANETARIUM_DOME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumDomeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="TesterAdmin",
            email="admin@admin.test",
            password="123465",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_planetarium_dome_post_available(self):
        payload = {
            "name": "forbidden",    # required
            "rows": 20,             # required
            "seats_in_row": 30      # required
        }
        response = self.client.post(PLANETARIUM_DOME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_planetarium_dome_delete_available(self):
        info = sample_planetarium_dome()

        res = self.client.delete(planetarium_dome_url(info.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
