# Apply Python 3.14 monkeypatch first before importing FastAPI/TestClient
import app

from fastapi.testclient import TestClient
from app.main import app as fastapi_app

client = TestClient(fastapi_app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_chat_basic():
    r = client.post("/chat/", json={"message": "What is the helmet fine in Delhi?"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    assert "194D" in res["content"] or "helmet" in res["content"].lower()

def test_chat_direct_db_lookup():
    # West Bengal helmet fine direct match
    r = client.post("/chat/", json={"message": "What is the helmet fine in West Bengal?"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    # Direct DB query answers are formatted with "Fine: " and "Section: "
    assert "Fine: " in res["content"]
    assert "Section: 194D" in res["content"]
    assert "West Bengal" in res["content"] or "Rules" in res["content"]

def test_chat_comparison():
    # Comparing helmet fine between Delhi and West Bengal
    r = client.post("/chat/", json={"message": "compare helmet fine in Delhi vs West Bengal"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    assert "Comparison" in res["content"]
    assert "Delhi" in res["content"]
    assert "West Bengal" in res["content"]
    assert "194D" in res["content"]

def test_chat_multi_violation():
    # Multiple violations
    r = client.post("/chat/", json={"message": "seatbelt and drunk driving fine in Delhi"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    assert "Combined Traffic Fines" in res["content"]
    assert "Seatbelt" in res["content"] or "seatbelt" in res["content"].lower()
    assert "Drunk Driving" in res["content"] or "drunk" in res["content"].lower()
    # Drunk driving is ₹10000, Seatbelt is ₹1000 -> Total should sum up
    assert "Total Aggregated Fine" in res["content"]

def test_calculator_endpoint_db_first():
    # Direct calculation query without AI
    r = client.post("/chat/calculate-challan", json={
        "violation": "no_helmet",
        "state": "West Bengal",
        "vehicle_type": "2W",
        "repeat": False
    })
    assert r.status_code == 200
    data = r.json()
    assert data["fine_inr"] == 1000
    assert data["section"] == "194D"
    assert "West Bengal" in data["explanation"] or "Rules" in data["explanation"]

def test_chat_conditional_sundays():
    r = client.post("/chat/", json={"message": "Is it legal to ride without helmet on Sundays?"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    content_lower = res["content"].lower()
    assert "helmet" in content_lower or "194" in content_lower

def test_chat_complex_evaluation_block():
    message = (
        "You are being evaluated as an Indian traffic law assistant. "
        "Answer the following queries accurately using proper law, fine, and section:\n"
        "1. What is the fine for riding without a helmet in West Bengal?\n"
        "2. Compare helmet fine in Delhi vs West Bengal.\n"
        "3. Calculate challan for overspeeding bike in Maharashtra (first offense).\n"
        "4. What happens if I drive without a license?\n"
        "5. Explain Section 194D in simple language.\n"
        "6. What is the fine for drunk driving?\n"
        "7. Helmet + no license + overspeeding — total fine?\n"
        "8. Is it legal to ride without helmet on Sundays?\n"
        "Rules: - Always include fine, section, and source"
    )
    r = client.post("/chat/", json={"message": message})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    content_lower = res["content"].lower()
    assert "helmet" in content_lower or "194d" in content_lower
    assert "license" in content_lower or "181" in content_lower
    assert "overspeed" in content_lower or "183" in content_lower
    assert "drunk" in content_lower or "185" in content_lower

def test_chat_greeting():
    r = client.post("/chat/", json={"message": "hello"})
    assert r.status_code == 200
    res = r.json()
    assert "content" in res
    content_lower = res["content"].lower()
    assert "hello" in content_lower or "assist" in content_lower or "drivelegal" in content_lower



