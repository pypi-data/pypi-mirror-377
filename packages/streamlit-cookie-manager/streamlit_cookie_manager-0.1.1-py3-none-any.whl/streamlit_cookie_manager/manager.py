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
        Minimal Encrypted Cookie Manager backed by a React Streamlit Component.
        Stores cookies in the browser (document.cookie) and encrypts values with Fernet.
        """
        self.prefix = prefix
        password = password or "default_secret_key"
        # Fernet requires 32-byte key
        key = base64.urlsafe_b64encode(password.encode("utf-8").ljust(32, b"0"))
        self.fernet = Fernet(key)

    def ready(self):
        """Check if component is ready (always True for minimal version)."""
        return True

    def get(self, key, default=None):
        cookies = _cookie_component(action="get") or {}
        enc_val = cookies.get(self.prefix + "_" + key)
        if not enc_val:
            return default
        try:
            return self.fernet.decrypt(enc_val.encode()).decode()
        except InvalidToken:
            return default

    def set(self, key, value):
        enc_val = self.fernet.encrypt(value.encode()).decode()
        _cookie_component(action="set", name=self.prefix + "_" + key, value=enc_val)

    def delete(self, key):
        _cookie_component(action="delete", name=self.prefix + "_" + key)

    def save(self):
        _cookie_component(action="save")