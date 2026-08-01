from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationApiTests(APITestCase):
    """
    Test registration, JWT authentication, token refresh, and profile access.
    """

    def setUp(self):
        """
        Prepare endpoint URLs and reusable user credentials.
        """

        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.profile_url = reverse("profile")

        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            username="lorian",
            email="lorian@example.com",
            first_name="Lorian",
            last_name="Afouma",
            password=self.password,
        )

        self.valid_registration_payload = {
            "username": "new-user",
            "email": "new-user@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "AnotherStrongPassword123!",
            "password_confirm": "AnotherStrongPassword123!",
        }

    def test_user_can_register_with_valid_data(self):
        """
        A new user account can be created with valid information.
        """

        response = self.client.post(
            self.register_url,
            self.valid_registration_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                username="new-user",
            ).exists()
        )

        created_user = User.objects.get(
            username="new-user"
        )

        self.assertEqual(
            created_user.email,
            "new-user@example.com",
        )

        self.assertTrue(
            created_user.check_password(
                "AnotherStrongPassword123!"
            )
        )

        self.assertNotIn(
            "password",
            response.data,
        )

        self.assertNotIn(
            "password_confirm",
            response.data,
        )

    def test_registration_normalizes_email_address(self):
        """
        Email addresses are trimmed and converted to lowercase.
        """

        payload = {
            **self.valid_registration_payload,
            "username": "normalized-user",
            "email": "  Normalized@Example.COM  ",
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        created_user = User.objects.get(
            username="normalized-user"
        )

        self.assertEqual(
            created_user.email,
            "normalized@example.com",
        )

    def test_registration_rejects_duplicate_username(self):
        """
        Django rejects an already existing username.
        """

        payload = {
            **self.valid_registration_payload,
            "username": self.user.username,
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "username",
            response.data,
        )

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        """
        Email uniqueness validation ignores letter casing.
        """

        payload = {
            **self.valid_registration_payload,
            "username": "another-user",
            "email": "LORIAN@EXAMPLE.COM",
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

        self.assertEqual(
            str(response.data["email"][0]),
            "An account already exists with this email address.",
        )

    def test_registration_rejects_mismatched_passwords(self):
        """
        Password confirmation must match the password.
        """

        payload = {
            **self.valid_registration_payload,
            "password_confirm": "DifferentPassword123!",
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password_confirm",
            response.data,
        )

    def test_registration_rejects_password_shorter_than_eight_characters(self):
        """
        Passwords must contain at least eight characters.
        """

        payload = {
            **self.valid_registration_payload,
            "password": "short",
            "password_confirm": "short",
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password",
            response.data,
        )

        self.assertIn(
            "password_confirm",
            response.data,
        )

    def test_user_can_login_with_valid_credentials(self):
        """
        Valid credentials return access and refresh JWT tokens.
        """

        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

        self.assertTrue(
            isinstance(response.data["access"], str)
        )

        self.assertTrue(
            isinstance(response.data["refresh"], str)
        )

    def test_login_rejects_invalid_password(self):
        """
        Invalid credentials return HTTP 401.
        """

        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn(
            "access",
            response.data,
        )

        self.assertNotIn(
            "refresh",
            response.data,
        )

    def test_login_rejects_unknown_username(self):
        """
        Unknown users cannot obtain JWT tokens.
        """

        response = self.client.post(
            self.login_url,
            {
                "username": "unknown-user",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_token_returns_new_access_token(self):
        """
        A valid refresh token generates a new access token.
        """

        login_response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

    def test_refresh_rejects_invalid_token(self):
        """
        An invalid refresh token is rejected.
        """

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_access_profile(self):
        """
        A valid access token grants access to the profile endpoint.
        """

        login_response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(
            self.profile_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.user.id,
        )

        self.assertEqual(
            response.data["username"],
            "lorian",
        )

        self.assertEqual(
            response.data["email"],
            "lorian@example.com",
        )

        self.assertEqual(
            response.data["first_name"],
            "Lorian",
        )

        self.assertEqual(
            response.data["last_name"],
            "Afouma",
        )

        self.assertIn(
            "date_joined",
            response.data,
        )

    def test_unauthenticated_user_cannot_access_profile(self):
        """
        Anonymous users receive HTTP 401 on the profile endpoint.
        """

        response = self.client.get(
            self.profile_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_rejects_invalid_access_token(self):
        """
        An invalid access token cannot access the profile endpoint.
        """

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-access-token"
        )

        response = self.client.get(
            self.profile_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_registration_ignores_invalid_authentication_header(self):
        """
        Registration remains public even with an invalid JWT header.
        """

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-access-token"
        )

        response = self.client.post(
            self.register_url,
            self.valid_registration_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )