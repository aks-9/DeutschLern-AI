"""Tests for authentication routes: register, login, logout, dashboard."""


REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
LOGOUT_URL = "/auth/logout"
DASHBOARD_URL = "/dashboard"

VALID_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
}


# -- Helpers ------------------------------------------------------------------

async def register(client, data=None):
    """Register a user and return the response."""
    return await client.post(REGISTER_URL, data=data or VALID_USER)


async def login(client, email=VALID_USER["email"], password=VALID_USER["password"]):
    """Log in and return the response."""
    return await client.post(LOGIN_URL, data={"email": email, "password": password})


async def register_and_login(client):
    """Register then log in; return the login response (cookie is set on client)."""
    await register(client)
    return await login(client)


# -- Registration -------------------------------------------------------------


async def test_register_redirects_to_login(client):
    """Successful registration should redirect to the login page."""
    response = await register(client)
    assert response.status_code == 302
    assert response.headers["location"] == "/auth/login"



async def test_register_duplicate_email_returns_400(client):
    """Registering with an already-used email should return 400."""
    await register(client)
    response = await register(client)
    assert response.status_code == 400



async def test_register_invalid_email_returns_400(client):
    """Registering with a malformed email should return 400."""
    response = await register(
        client,
        data={
            "username": "testuser",
            "email": "not-an-email",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 400



async def test_register_short_password_returns_400(client):
    """Registering with a password under 8 characters should return 400."""
    response = await register(
        client,
        data={
            "username": "testuser",
            "email": "short@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 400


# -- Login --------------------------------------------------------------------


async def test_login_success_redirects_to_dashboard(client):
    """Valid credentials should redirect to /dashboard and set a cookie."""
    await register(client)
    response = await login(client)
    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"
    assert "access_token" in response.cookies



async def test_login_wrong_password_returns_401(client):
    """Wrong password should return 401."""
    await register(client)
    response = await login(client, password="wrongpassword")
    assert response.status_code == 401



async def test_login_unknown_email_returns_401(client):
    """Unregistered email should return 401."""
    response = await login(client, email="nobody@example.com")
    assert response.status_code == 401


# -- Dashboard ----------------------------------------------------------------


async def test_dashboard_requires_authentication(client):
    """Visiting /dashboard without a cookie should return 401."""
    response = await client.get(DASHBOARD_URL)
    assert response.status_code == 401



async def test_dashboard_redirects_browser_to_login(client):
    """A browser page request (Accept: text/html) without a cookie should
    redirect to the login page instead of showing raw JSON."""
    response = await client.get(
        DASHBOARD_URL, headers={"Accept": "text/html"}
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/auth/login"



async def test_htmx_request_still_gets_401(client):
    """An HTMX request must still receive 401, not a redirect — HTMX would
    otherwise swap the login page HTML into the target element."""
    response = await client.get(
        DASHBOARD_URL,
        headers={"Accept": "text/html", "HX-Request": "true"},
    )
    assert response.status_code == 401



async def test_dashboard_accessible_when_logged_in(client):
    """Visiting /dashboard with a valid cookie should return 200."""
    await register_and_login(client)
    response = await client.get(DASHBOARD_URL)
    assert response.status_code == 200
    assert "testuser" in response.text


# -- Logout -------------------------------------------------------------------


async def test_logout_clears_cookie_and_redirects(client):
    """Logout should delete the access_token cookie and redirect to login."""
    await register_and_login(client)
    response = await client.get(LOGOUT_URL)
    assert response.status_code == 302
    assert response.headers["location"] == "/auth/login"
    # Cookie should be deleted (max-age=0 or empty value)
    assert response.cookies.get("access_token", "") == ""



async def test_dashboard_inaccessible_after_logout(client):
    """After logout, /dashboard should return 401."""
    await register_and_login(client)
    await client.get(LOGOUT_URL)
    response = await client.get(DASHBOARD_URL)
    assert response.status_code == 401
