import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from cryptography.fernet import Fernet, InvalidToken

# Declare Streamlit component
_cookie_component = components.declare_component(
    "cookie_manager",
    path=os.path.join(os.path.dirname(__file__), "frontend", "dist")
)

class EncryptedCookieManager:
    def __init__(self, prefix="st_cookie", password=None):
        """
        Encrypted Cookie Manager backed by a Streamlit React Component.
        Stores cookies in the browser (document.cookie) and encrypts values with Fernet.
        """
        self.prefix = prefix
        password = password or "default_secret_key"
        key = base64.urlsafe_b64encode(password.encode("utf-8").ljust(32, b"0"))
        self.fernet = Fernet(key)

    def ready(self):
        """Check if the component is ready (always True in this minimal version)."""
        return True

    def get(self, key: str, default=None):
        """Retrieve an encrypted cookie value (or default if missing/invalid)."""
        cookies = _cookie_component(action="get", key=f"get_{key}") or {}
        enc_val = cookies.get(self.prefix + "_" + key)
        if not enc_val:
            return default
        try:
            return self.fernet.decrypt(enc_val.encode()).decode()
        except InvalidToken:
            return default

    def set(self, key: str, value: str):
        """Set an encrypted cookie value in the browser."""
        enc_val = self.fernet.encrypt(value.encode()).decode()
        _cookie_component(
            action="set",
            name=self.prefix + "_" + key,
            value=enc_val,
            key=f"set_{key}"
        )

    def delete(self, key: str):
        """Delete a cookie by name."""
        _cookie_component(
            action="delete",
            name=self.prefix + "_" + key,
            key=f"del_{key}"
        )

    def save(self):
        """Trigger cookie persistence (no-op in minimal version)."""
        _cookie_component(action="save", key="save")

    # --- Dict-style support ---
    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: str):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.delete(key)