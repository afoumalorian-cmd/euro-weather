from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather.models import FavoriteCity


User = get_user_model()


class FavoriteCityApiTests(APITestCase):
    """
    Test favorite city API behavior and user isolation.
    """

    def setUp(self):
        """
        Create two users and resolve favorite city endpoint URLs.
        """

        self.user = User.objects.create_user(
            username="lorian",
            email="lorian@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password="StrongPassword123!",
        )

        self.list_url = reverse(
            "weather:favorite-city-list-create"
        )

        self.favorite_payload = {
            "city": "Paris",
            "country": "France",
            "latitude": 48.8566,
            "longitude": 2.3522,
        }

    def authenticate(self, user=None):
        """
        Authenticate API requests without manually generating a JWT.
        """

        self.client.force_authenticate(
            user=user or self.user
        )

    def create_favorite(
        self,
        *,
        user=None,
        city="Paris",
        country="France",
    ):
        """
        Create a favorite city directly in the test database.
        """

        return FavoriteCity.objects.create(
            user=user or self.user,
            city=city,
            country=country,
            latitude=Decimal("48.856600"),
            longitude=Decimal("2.352200"),
        )

    def test_authenticated_user_can_create_favorite_city(self):
        """
        An authenticated user can save a favorite city.
        """

        self.authenticate()

        response = self.client.post(
            self.list_url,
            self.favorite_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            FavoriteCity.objects.count(),
            1,
        )

        favorite = FavoriteCity.objects.get()

        self.assertEqual(
            favorite.user,
            self.user,
        )
        self.assertEqual(
            favorite.city,
            "Paris",
        )
        self.assertEqual(
            favorite.country,
            "France",
        )
        self.assertEqual(
            favorite.latitude,
            Decimal("48.856600"),
        )
        self.assertEqual(
            favorite.longitude,
            Decimal("2.352200"),
        )

    def test_unauthenticated_user_cannot_create_favorite_city(self):
        """
        Anonymous users receive HTTP 401.
        """

        response = self.client.post(
            self.list_url,
            self.favorite_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            FavoriteCity.objects.count(),
            0,
        )

    def test_authenticated_user_can_list_own_favorites(self):
        """
        A user only receives favorite cities they own.
        """

        self.create_favorite(
            user=self.user,
            city="Paris",
            country="France",
        )

        self.create_favorite(
            user=self.other_user,
            city="Berlin",
            country="Germany",
        )

        self.authenticate()

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["city"],
            "Paris",
        )

        self.assertEqual(
            response.data[0]["country"],
            "France",
        )

    def test_unauthenticated_user_cannot_list_favorites(self):
        """
        Anonymous users cannot read favorite cities.
        """

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_duplicate_favorite_city_is_rejected(self):
        """
        The same user cannot save the same city twice.
        """

        self.create_favorite()

        self.authenticate()

        response = self.client.post(
            self.list_url,
            self.favorite_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            FavoriteCity.objects.filter(
                user=self.user,
            ).count(),
            1,
        )

    def test_duplicate_check_is_case_insensitive(self):
        """
        Duplicate validation ignores letter casing.
        """

        self.create_favorite(
            city="Paris",
            country="France",
        )

        self.authenticate()

        response = self.client.post(
            self.list_url,
            {
                **self.favorite_payload,
                "city": "PARIS",
                "country": "france",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_different_users_can_save_the_same_city(self):
        """
        Each user can independently save the same city.
        """

        self.create_favorite(
            user=self.other_user,
        )

        self.authenticate(self.user)

        response = self.client.post(
            self.list_url,
            self.favorite_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            FavoriteCity.objects.filter(
                city="Paris",
                country="France",
            ).count(),
            2,
        )

    def test_user_can_retrieve_own_favorite_city(self):
        """
        A user can retrieve a favorite city they own.
        """

        favorite = self.create_favorite()

        detail_url = reverse(
            "weather:favorite-city-detail",
            kwargs={
                "pk": favorite.pk,
            },
        )

        self.authenticate()

        response = self.client.get(
            detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            favorite.id,
        )

    def test_user_cannot_retrieve_another_users_favorite(self):
        """
        Another user's favorite is hidden with HTTP 404.
        """

        favorite = self.create_favorite(
            user=self.other_user,
        )

        detail_url = reverse(
            "weather:favorite-city-detail",
            kwargs={
                "pk": favorite.pk,
            },
        )

        self.authenticate(self.user)

        response = self.client.get(
            detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_can_delete_own_favorite_city(self):
        """
        A user can delete a favorite city they own.
        """

        favorite = self.create_favorite()

        detail_url = reverse(
            "weather:favorite-city-detail",
            kwargs={
                "pk": favorite.pk,
            },
        )

        self.authenticate()

        response = self.client.delete(
            detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            FavoriteCity.objects.filter(
                pk=favorite.pk,
            ).exists()
        )

    def test_user_cannot_delete_another_users_favorite(self):
        """
        A user cannot delete another user's favorite city.
        """

        favorite = self.create_favorite(
            user=self.other_user,
        )

        detail_url = reverse(
            "weather:favorite-city-detail",
            kwargs={
                "pk": favorite.pk,
            },
        )

        self.authenticate(self.user)

        response = self.client.delete(
            detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            FavoriteCity.objects.filter(
                pk=favorite.pk,
            ).exists()
        )

    def test_city_and_country_are_trimmed(self):
        """
        The serializer removes unnecessary surrounding whitespace.
        """

        self.authenticate()

        response = self.client.post(
            self.list_url,
            {
                **self.favorite_payload,
                "city": "  Paris  ",
                "country": "  France  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        favorite = FavoriteCity.objects.get()

        self.assertEqual(
            favorite.city,
            "Paris",
        )
        self.assertEqual(
            favorite.country,
            "France",
        )