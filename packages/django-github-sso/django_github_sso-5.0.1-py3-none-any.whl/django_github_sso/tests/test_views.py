import pytest
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from django_github_sso.tests.conftest import SECRET_PATH
from example_github_app.settings import get_sso_config

ROUTE_NAME = "django_github_sso:oauth_callback"


pytestmark = pytest.mark.django_db()


class MyBackend(ModelBackend):
    """Simple test for custom authentication backend"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        return super().authenticate(request, username, password, **kwargs)


def test_start_login(client, github_mock):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login") + "?next=/secret/"
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == SECRET_PATH


def test_start_login_none_next_param(client, github_mock):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login")
    response = client.get(url)
    next_url = get_sso_config(response.wsgi_request).get("next_url")

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == reverse(next_url)


@pytest.mark.parametrize(
    "test_parameter",
    [
        "bad-domain.com/secret/",
        "www.bad-domain.com/secret/",
        "//bad-domain.com/secret/",
        "http://bad-domain.com/secret/",
        "https://malicious.example.com/secret/",
    ],
)
def test_exploit_redirect(client, github_mock, test_parameter):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login") + f"?next={test_parameter}"
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == SECRET_PATH


def test_github_sso_disabled(settings, client):
    # Arrange
    settings.GITHUB_SSO_ENABLED = False

    # Act
    response = client.get(reverse(ROUTE_NAME))

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "GitHub SSO not enabled." in [
        m.message for m in get_messages(response.wsgi_request)
    ]


def test_missing_code(client):
    # Act
    response = client.get(reverse(ROUTE_NAME))

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "Authorization Code not received from SSO." in [
        m.message for m in get_messages(response.wsgi_request)
    ]


@pytest.mark.parametrize("querystring", ["?code=1234", "?code=1234&state=bad_dog"])
def test_bad_state(client, querystring):
    # Arrange
    session = client.session
    session.update({"sso_state": "good_dog"})
    session.save()

    # Act
    url = reverse(ROUTE_NAME) + querystring
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "State Mismatch. Time expired?" in [
        m.message for m in get_messages(response.wsgi_request)
    ]


def test_invalid_email(
    client_with_session, settings, callback_url, github_mock, email_data_mock
):
    # Arrange
    settings.GITHUB_SSO_ALLOWABLE_DOMAINS = ["foobar.com"]

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert (
        f"Email address not allowed: {email_data_mock.email}. "
        f"Please contact your administrator."
        in [m.message for m in get_messages(response.wsgi_request)]
    )


def test_inactive_user(
    client_with_session, callback_url, github_mock, auth_user_mock, email_data_mock
):
    # Arrange
    User.objects.update_or_create(
        username=auth_user_mock.login,
        email=email_data_mock.email,
        defaults={
            "is_active": False,
        },
    )

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert User.objects.get(email=email_data_mock.email).is_active is False


@pytest.mark.parametrize(
    "allowable_domains",
    [
        ["dailybugle.info"],
        ["*"],
    ],
)
def test_new_user_login(
    client_with_session, callback_url, github_mock, settings, allowable_domains
):
    # Arrange
    settings.GITHUB_SSO_ALLOWABLE_DOMAINS = allowable_domains
    User.objects.all().delete()
    assert User.objects.count() == 0

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert response.url == SECRET_PATH
    assert response.wsgi_request.user.is_authenticated is True


def test_existing_user_login(
    client_with_session,
    settings,
    github_mock,
    auth_user_mock,
    email_data_mock,
    callback_url,
):
    # Arrange
    existing_user, _ = User.objects.update_or_create(
        username=auth_user_mock.login,
        email=email_data_mock.email,
        defaults={
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    settings.GITHUB_SSO_AUTO_CREATE_USERS = False

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert response.url == SECRET_PATH
    assert response.wsgi_request.user.is_authenticated is True
    assert response.wsgi_request.user.email == existing_user.email


def test_missing_user_login(client_with_session, settings, callback_url, github_mock):
    # Arrange
    settings.GITHUB_SSO_AUTO_CREATE_USERS = False

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert response.url == "/"
    assert response.wsgi_request.user.is_authenticated is False


def test_new_user_without_name(client_with_session, callback_url, github_mock_no_name):
    # Arrange
    User.objects.all().delete()
    assert User.objects.count() == 0

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert response.url == SECRET_PATH
    assert response.wsgi_request.user.is_authenticated is True
