import os
import sqlite3

import whatsapp


def test_db_paths_are_local():
    """Assert that MESSAGES_DB_PATH and WHATSMEOW_DB_PATH resolve to local absolute filesystem paths."""
    messages_db = whatsapp.MESSAGES_DB_PATH
    whatsmeow_db = whatsapp.WHATSMEOW_DB_PATH

    # Prove that the paths are absolute filesystem paths
    assert os.path.isabs(messages_db), f"MESSAGES_DB_PATH must be an absolute path: {messages_db}"
    assert os.path.isabs(whatsmeow_db), f"WHATSMEOW_DB_PATH must be an absolute path: {whatsmeow_db}"

    # Prove that they do not use remote database URI schemes
    forbidden_prefixes = ("http://", "https://", "mongodb://", "postgres://", "mysql://", "sqlite:///")
    assert not messages_db.startswith(forbidden_prefixes), f"MESSAGES_DB_PATH cannot be a remote URI: {messages_db}"
    assert not whatsmeow_db.startswith(forbidden_prefixes), f"WHATSMEOW_DB_PATH cannot be a remote URI: {whatsmeow_db}"

    # Prove that we are using the standard local sqlite3 library
    assert whatsapp.sqlite3 is sqlite3
