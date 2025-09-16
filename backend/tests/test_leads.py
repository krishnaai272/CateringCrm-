import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def sample_lead():
    return {
        "name": "John Doe",
        "phone": "9876543210",
        "email": "john@example.com",
        "event_type": "Wedding",
        "guests_count": 150,
        "event_date": "2025-12-20",
        "venue": "Chennai Hall",
        "notes": "VIP guest present"
    }


def test_create_lead(sample_lead):
    response = client.post("/leads/", json=sample_lead)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_lead["name"]
    assert data["phone"] == sample_lead["phone"]


def test_get_leads():
    response = client.get("/leads/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_lead(sample_lead):
    # Create lead first
    create_resp = client.post("/leads/", json=sample_lead)
    lead_id = create_resp.json()["id"]

    update_data = {"stage": "Contacted"}
    response = client.put(f"/leads/{lead_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["stage"] == "Contacted"


def test_delete_lead(sample_lead):
    # Create lead first
    create_resp = client.post("/leads/", json=sample_lead)
    lead_id = create_resp.json()["id"]

    response = client.delete(f"/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Lead deleted successfully"

def delete_lead(lead_id):
    """Finds a lead by its ID and removes it from the in-memory list."""
    lead_to_delete = next((l for l in st.session_state.leads if l['id'] == lead_id), None)
    
    if lead_to_delete:
        st.session_state.leads.remove(lead_to_delete)
        st.toast(f"Lead '{lead_to_delete['name']}' has been deleted.", icon="🗑️")
        st.rerun()