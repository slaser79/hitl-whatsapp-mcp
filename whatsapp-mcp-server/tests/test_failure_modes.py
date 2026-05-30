import requests

import main
import whatsapp


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text="OK"):
        self.status_code = status_code
        self._payload = payload or {"success": True, "message": "sent", "path": "/tmp/media.jpg"}
        self.text = text

    def json(self):
        return self._payload


def test_bridge_unavailable(monkeypatch, tmp_path):
    """If the bridge is unreachable, tools return bridge_unavailable error."""

    def fake_get_fail(url, headers=None, timeout=None):
        raise requests.ConnectionError("Connection refused")

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_fail)

    # 1) send_message
    res = main.send_message(recipient="12025551234", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]

    # 2) send_file
    # Create a dummy file to pass validation using tmp_path
    dummy_file = tmp_path / "dummy_file.ogg"
    dummy_file.write_text("dummy content")
    media_path = str(dummy_file)

    res = main.send_file(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]

    # 3) send_audio_message
    res = main.send_audio_message(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]

    # 4) download_media
    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]


def test_whatsapp_session_expired(monkeypatch, tmp_path):
    """If the session is expired, tools return whatsapp_session_expired error."""

    # Mock /api/health to return 503 Service Unavailable / disconnected
    def fake_get_disconnected(url, headers=None, timeout=None):
        return DummyResponse(status_code=503, payload={"status": "disconnected", "connected": False})

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_disconnected)

    # 1) send_message
    res = main.send_message(recipient="12025551234", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "whatsapp_session_expired"
    assert "whatsapp_session_expired" in res["message"]

    # 2) send_file
    dummy_file = tmp_path / "dummy_file.ogg"
    dummy_file.write_text("dummy content")
    media_path = str(dummy_file)

    res = main.send_file(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "whatsapp_session_expired"
    assert "whatsapp_session_expired" in res["message"]

    # 3) send_audio_message
    res = main.send_audio_message(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "whatsapp_session_expired"
    assert "whatsapp_session_expired" in res["message"]

    # 4) download_media
    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "whatsapp_session_expired"
    assert "whatsapp_session_expired" in res["message"]


def test_chat_not_found_on_send(monkeypatch, tmp_path):
    """If chat is invalid/unknown (400 Bad Request from bridge), send tools return chat_not_found."""

    # Health check passes
    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    # Send returns 400 Bad Request
    def fake_post_bad_request(url, json, headers=None):
        return DummyResponse(status_code=400, text="Error resolving recipient: JID format invalid")

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_bad_request)

    res = main.send_message(recipient="invalid-recipient", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "chat_not_found"
    assert "chat_not_found" in res["message"]

    dummy_file = tmp_path / "dummy_file.ogg"
    dummy_file.write_text("dummy content")
    media_path = str(dummy_file)

    res = main.send_file(recipient="invalid-recipient", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "chat_not_found"
    assert "chat_not_found" in res["message"]

    res = main.send_audio_message(recipient="invalid-recipient", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "chat_not_found"
    assert "chat_not_found" in res["message"]


def test_chat_not_found_on_download(monkeypatch):
    """If message/chat is invalid/unknown on download (400), download_media returns chat_not_found."""

    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    def fake_post_download_fail(url, json, headers=None):
        return DummyResponse(
            status_code=400, payload={"success": False, "message": "Failed to download media: message not found"}
        )

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_download_fail)

    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "chat_not_found"
    assert "chat_not_found" in res["message"]


def test_local_file_not_found():
    """If the local media file is missing, send tools return file_not_found."""
    res = main.send_file(recipient="12025551234", media_path="nonexistent_file.jpg")
    assert res["success"] is False
    assert res["error_code"] == "file_not_found"
    assert "file_not_found" in res["message"]

    res = main.send_audio_message(recipient="12025551234", media_path="nonexistent_file.ogg")
    assert res["success"] is False
    assert res["error_code"] == "file_not_found"
    assert "file_not_found" in res["message"]


def test_bridge_unauthorized(monkeypatch, tmp_path):
    """If the bridge returns HTTP 401, tools return bridge_unauthorized."""

    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    def fake_post_unauthorized(url, json, headers=None):
        return DummyResponse(status_code=401, text="Unauthorized")

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_unauthorized)

    res = main.send_message(recipient="12025551234", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unauthorized"
    assert "bridge_unauthorized" in res["message"]

    dummy_file = tmp_path / "dummy_file.ogg"
    dummy_file.write_text("dummy content")
    media_path = str(dummy_file)

    res = main.send_file(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "bridge_unauthorized"
    assert "bridge_unauthorized" in res["message"]

    res = main.send_audio_message(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "bridge_unauthorized"
    assert "bridge_unauthorized" in res["message"]

    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unauthorized"
    assert "bridge_unauthorized" in res["message"]


def test_audio_conversion_failure(tmp_path):
    """If ffmpeg conversion fails, send_audio_message returns internal_error."""
    # We pass a non-ogg file that exists but contains dummy data. Since it's not a valid audio file,
    # conversion will fail (either because ffmpeg is missing or it fails to parse it).
    dummy_file = tmp_path / "dummy_invalid_audio.jpg"
    dummy_file.write_text("not an audio file")
    media_path = str(dummy_file)

    res = main.send_audio_message(recipient="12025551234", media_path=media_path)
    assert res["success"] is False
    assert res["error_code"] == "internal_error"
    assert "internal_error" in res["message"]


def test_health_check_200_disconnected(monkeypatch):
    """If /api/health returns 200 but connected is False, check_bridge_health raises SessionExpiredError."""

    def fake_get_disconnected_200(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "disconnected", "connected": False})

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_disconnected_200)

    res = main.send_message(recipient="12025551234", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "whatsapp_session_expired"
    assert "whatsapp_session_expired" in res["message"]


def test_download_media_non_json(monkeypatch):
    """If download_media receives a non-JSON 200 response, it is caught as bridge_unavailable."""

    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    class MalformedResponse(DummyResponse):
        def json(self):
            import json

            raise json.JSONDecodeError("Expecting value", "", 0)

    def fake_post_malformed(url, json, headers=None):
        return MalformedResponse(status_code=200, text="Not a JSON response")

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_malformed)

    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]


def test_bridge_500_status_code(monkeypatch):
    """If the bridge returns HTTP 500, tools return bridge_unavailable instead of chat_not_found."""

    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    def fake_post_500(url, json, headers=None):
        return DummyResponse(status_code=500, text="Internal Server Error")

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_500)

    res = main.send_message(recipient="12025551234", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]


def test_download_media_success_false(monkeypatch):
    """If download_media receives response 200 but success is False, it is caught as bridge_unavailable."""

    def fake_get_ok(url, headers=None, timeout=None):
        return DummyResponse(status_code=200, payload={"status": "ok", "connected": True})

    def fake_post_success_false(url, json, headers=None):
        return DummyResponse(status_code=200, payload={"success": False, "message": "Failed to download media"})

    monkeypatch.setattr(whatsapp.requests, "get", fake_get_ok)
    monkeypatch.setattr(whatsapp.requests, "post", fake_post_success_false)

    res = main.download_media(message_id="msg-id", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "bridge_unavailable"
    assert "bridge_unavailable" in res["message"]


def test_invalid_parameters():
    """If required parameters are missing/invalid, tools return invalid_parameters error."""
    # 1) send_message with missing recipient
    res = main.send_message(recipient="", message="hello")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Recipient must be provided" in res["message"]

    # 2) send_file with missing recipient
    res = main.send_file(recipient="", media_path="dummy.ogg")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Recipient must be provided" in res["message"]

    # 3) send_file with missing media_path
    res = main.send_file(recipient="12025551234", media_path="")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Media path must be provided" in res["message"]

    # 4) send_audio_message with missing recipient
    res = main.send_audio_message(recipient="", media_path="dummy.ogg")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Recipient must be provided" in res["message"]

    # 5) send_audio_message with missing media_path
    res = main.send_audio_message(recipient="12025551234", media_path="")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Media path must be provided" in res["message"]

    # 6) download_media with missing message_id
    res = main.download_media(message_id="", chat_jid="12025551234@s.whatsapp.net")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Message ID and Chat JID are required" in res["message"]

    # 7) download_media with missing chat_jid
    res = main.download_media(message_id="msg-id", chat_jid="")
    assert res["success"] is False
    assert res["error_code"] == "invalid_parameters"
    assert "Message ID and Chat JID are required" in res["message"]
