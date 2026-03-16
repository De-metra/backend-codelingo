import pytest

@pytest.mark.asyncio
class TestAuthEndpoints:

    async def test_get_levels_authorized(self, client, auth_header):
        response = await client.get("/api/levels/1/", headers=auth_header)

        assert response.status_code != 401
        assert response.status_code != 403

    async def test_get_levels_unauthorized(self, client):
        response = await client.get("/api/levels/1/")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    async def test_get_levels_bad_token(self, client):
        auth_header = {"Authorization": "Bearer not-a-real-token"}
        response = await client.get("/api/levels/1/", headers=auth_header)

        assert response.status_code == 401

    async def test_login_success(self, client):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "12345"
            }
        )

        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "12345"
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


    async def test_login_wrong_password(self, client):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "test",
                "email": "same@example.com",
                "password": "12345"
            }
        )

        response = await client.post(
            "/api/auth/login",
            json={
                "email": "same@example.com",
                "password": "wrong password"
            }
        )

        assert response.status_code == 401


    async def test_register_success(self, client):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "test",
                "email": "existed@example.com",
                "password": "12345"
            }
        )

        assert response.status_code == 201

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    
    async def test_register_existed_email(self, client):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "test",
                "email": "existed@example.com",
                "password": "12345"
            }
        )

        response1 = await client.post(
            "/api/auth/register",
            json={
                "username": "test",
                "email": "existed@example.com",
                "password": "12345"
            }
        )

        assert response1.status_code == 409