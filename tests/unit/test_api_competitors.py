from fastapi.testclient import TestClient
from dram_sentry.web.api.competitors import router

client = TestClient(router)

def test_competitors_endpoint_json():
    response = client.get("/competitors?format=json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

def test_competitors_endpoint_csv():
    response = client.get("/competitors?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

def test_competitors_endpoint_invalid_format():
    response = client.get("/competitors?format=xml")
    assert response.status_code == 400
    assert "Invalid format" in response.json()["detail"]

def test_competitors_endpoint_server_error():
    # Mock analytics to raise an exception
    with patch("dram_sentry.analytics.competitor.CompetitorAnalytics.get_top_suppliers", side_effect=Exception()):
        response = client.get("/competitors?format=json")
        assert response.status_code == 500