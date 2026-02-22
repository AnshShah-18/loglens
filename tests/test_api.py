from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app


TEST_DB_PATH = Path("test_loglens.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_module():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db


def teardown_module():
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_post_includes_cors_header():
    response = client.post(
        "/api/upload",
        files={"file": ("cors.log", "INFO cors check", "text/plain")},
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_upload_and_pattern_endpoints():
    demo_log = "\n".join(
        [
            'ERROR db connection failed host=10.1.2.3 request_id=550e8400-e29b-41d4-a716-446655440000 path=/srv/app/config.yml',
            'ERROR payment timeout order=101 trace=zzz999yyy888 key=/users/ansh/photos/abc.jpg msg="gateway timeout"',
        ]
    )
    upload_1_response = client.post(
        "/api/upload",
        files={"file": ("samples/demo.log", demo_log, "text/plain")},
    )
    assert upload_1_response.status_code == 200
    upload_1_id = upload_1_response.json()["id"]

    upload_1_patterns_response = client.get(f"/api/uploads/{upload_1_id}/patterns")
    assert upload_1_patterns_response.status_code == 200
    upload_1_patterns = upload_1_patterns_response.json()["patterns"]
    assert upload_1_patterns
    assert all(pattern["is_new"] is True for pattern in upload_1_patterns)

    demo_new_log = "\n".join(
        [
            'ERROR db connection failed host=10.1.2.4 request_id=123e4567-e89b-12d3-a456-426614174000 path=/srv/app/config.yml',
            'ERROR payment timeout order=202 trace=aaa111bbb222 key=/users/ansh/photos/def.jpg msg="gateway timeout"',
            r'ERROR s3 upload failed path=C:\app\logs\current.log ip=192.168.10.7 job=9912 msg="cannot write"',
        ]
    )
    upload_2_response = client.post(
        "/api/upload",
        files={"file": ("samples/demo_new.log", demo_new_log, "text/plain")},
    )
    assert upload_2_response.status_code == 200
    upload_2_payload = upload_2_response.json()
    assert upload_2_payload["filename"] == "samples/demo_new.log"
    assert upload_2_payload["pattern_count"] == 3

    upload_2_id = upload_2_payload["id"]
    patterns_response = client.get(f"/api/uploads/{upload_2_id}/patterns")
    assert patterns_response.status_code == 200
    patterns_payload = patterns_response.json()["patterns"]
    assert len(patterns_payload) == 3

    db_connection_pattern = next(
        pattern for pattern in patterns_payload if "db connection failed" in pattern["pattern_text"]
    )
    payment_timeout_pattern = next(
        pattern for pattern in patterns_payload if "payment timeout" in pattern["pattern_text"]
    )
    s3_failed_pattern = next(
        pattern for pattern in patterns_payload if "s3 upload failed" in pattern["pattern_text"]
    )

    assert db_connection_pattern["is_new"] is False
    assert payment_timeout_pattern["is_new"] is False
    assert s3_failed_pattern["is_new"] is True
    assert "<PATH>" in s3_failed_pattern["pattern_text"]
    assert "<IP>" in s3_failed_pattern["pattern_text"]
    assert "\"<STR>\"" in s3_failed_pattern["pattern_text"]
    assert "<NUM>" in s3_failed_pattern["pattern_text"]
    assert "<UUID>" in db_connection_pattern["pattern_text"]
    assert "<HEX>" in payment_timeout_pattern["pattern_text"]
    assert "trace=<HEX>" in payment_timeout_pattern["pattern_text"]
    assert "key=<PATH>" in payment_timeout_pattern["pattern_text"]

    pattern_response = client.get(f"/api/patterns/{db_connection_pattern['id']}")
    assert pattern_response.status_code == 200
    pattern_payload = pattern_response.json()
    assert pattern_payload["count"] == 1
    assert pattern_payload["upload_id"] == upload_2_id


def test_not_found_paths():
    upload_response = client.get("/api/uploads/999999/patterns")
    assert upload_response.status_code == 404
    assert upload_response.json()["detail"] == "Upload not found"

    pattern_response = client.get("/api/patterns/999999")
    assert pattern_response.status_code == 404
    assert pattern_response.json()["detail"] == "Pattern not found"
