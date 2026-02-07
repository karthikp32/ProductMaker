"""Tests for training sessions API."""
from datetime import date

def test_create_session(client):
    response = client.post("/api/v1/sessions", json={
        "session_date": str(date.today()), "sport_type": "running", "duration_minutes": 45
    })
    assert response.status_code == 201
    assert response.json()["sport_type"] == "running"

def test_list_sessions(client):
    client.post("/api/v1/sessions", json={"session_date": str(date.today()), "sport_type": "cycling", "duration_minutes": 60})
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    assert "sessions" in response.json()
