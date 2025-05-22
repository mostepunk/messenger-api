class TestHealthcheckAPI:
    async def test_health_api_200(self, app, client):
        response = await client.get(app.url_path_for("healthcheck:get"))
        assert response.status_code == 200

    async def test_health_api_500(self, incorrect_app, client):
        response = await client.get(incorrect_app.url_path_for("healthcheck:get"))
        resp_json = response.json()
        assert response.status_code == 500
        assert (
            'database "database_not_exist__testing" does not exist'
            in resp_json["error"]
        )
