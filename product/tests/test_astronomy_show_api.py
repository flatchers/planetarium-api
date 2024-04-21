from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from product.models import AstronomyShow, ShowTheme
from product.serializers import AstronomyShowSerializer, AstronomyShowListSerializer, AstronomyShowDetailSerializer

ASTRONOMY_URL = reverse("planetarium:astronomyshow-list")


def astronomy_show_detail(show_id):
    return reverse("planetarium:astronomyshow-detail", args=(show_id,))


def sample_astronomy(**params):
    default = {
        "title": "Anything",
    }
    default.update(params)
    return AstronomyShow.objects.create(**default)


class UnAuthenticatedAstronomyShowTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123"
        )
        self.client.force_authenticate(self.user)

    def test_astronomy_show_list(self):
        sample_astronomy()
        show_with_themes = sample_astronomy()

        theme1 = ShowTheme.objects.create(name="test1")
        theme2 = ShowTheme.objects.create(name="test2")

        show_with_themes.show_themes.add(theme1)
        show_with_themes.show_themes.add(theme2)

        res = self.client.get(ASTRONOMY_URL)
        astronomies = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(astronomies, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_astronomy_by_themes(self):
        astronomy_without_themes = sample_astronomy()
        astronomy_with_themes1 = sample_astronomy(title="test11")
        astronomy_with_themes2 = sample_astronomy(title="test12")

        theme1 = ShowTheme.objects.create(name="test1")
        theme2 = ShowTheme.objects.create(name="test2")

        astronomy_with_themes1.show_themes.add(theme1)
        astronomy_with_themes2.show_themes.add(theme2)

        res = self.client.get(ASTRONOMY_URL, {"show_themes": f"{theme1.id},{theme2.id}"})
        serializer_without_themes = AstronomyShowListSerializer(astronomy_without_themes)
        serializer_with_themes1 = AstronomyShowListSerializer(astronomy_with_themes1)
        serializer_with_themes2 = AstronomyShowListSerializer(astronomy_with_themes2)
        self.assertIn(serializer_with_themes1.data, res.data)
        self.assertIn(serializer_with_themes2.data, res.data)
        self.assertNotIn(serializer_without_themes.data, res.data)

    def test_astronomy_detail(self):
        astronomy_show = sample_astronomy()
        astronomy_show.show_themes.add(ShowTheme.objects.create(name="Test astronomy"))
        res = self.client.get(astronomy_show_detail(astronomy_show.id))
        serializer = AstronomyShowDetailSerializer(astronomy_show)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_show_forbidden(self):
        payload = {"title": "test forbidden"}
        res = self.client.post(ASTRONOMY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_admin",
            email="test@admin.user",
            password="123465",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_astronomy_show_create(self):
        payload = {"title": "test forbidden"}
        res = self.client.post(ASTRONOMY_URL, payload)
        astronomy = AstronomyShow.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astronomy, key))
