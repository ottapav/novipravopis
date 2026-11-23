from fastapi.testclient import TestClient

from app.main import MAX_CHARS, app

client = TestClient(app)


def test_convert_prevede_text():
    res = client.post("/api/convert", json={"text": "Byl systém."})
    assert res.status_code == 200
    data = res.json()
    assert data["text"] == "Bil systém."
    assert data["stats"]["changedLetters"] == 1
    assert data["stats"]["foreignKept"] == 1
    assert isinstance(data["segments"], list)


def test_ceske_znaky_nejsou_escapovane():
    res = client.post("/api/convert", json={"text": "sýr"})
    assert "sír" in res.content.decode("utf-8")


def test_chybejici_nebo_spatny_text_vrati_400():
    assert client.post("/api/convert", json={}).status_code == 400
    assert client.post("/api/convert", json={"text": 5}).status_code == 400
    bad = client.post(
        "/api/convert",
        content="{špatný json".encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    assert bad.status_code == 400
    assert "error" in bad.json()


def test_prilis_dlouhy_text_vrati_413():
    res = client.post("/api/convert", json={"text": "a" * (MAX_CHARS + 1)})
    assert res.status_code == 413
    assert "error" in res.json()


def test_prilis_velke_telo_vrati_413():
    res = client.post("/api/convert", json={"text": "a" * 1_100_000})
    assert res.status_code == 413


def test_staticke_soubory_a_healthcheck():
    index = client.get("/")
    assert index.status_code == 200
    assert "Noví pravopis" in index.text
    assert client.get("/app.js").status_code == 200
    assert client.get("/style.css").status_code == 200
    assert client.get("/healthz").text == "ok"
    assert client.get("/app/main.py").status_code == 404


def test_bezpecnostni_hlavicky():
    res = client.get("/")
    assert res.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in res.headers["content-security-policy"]
