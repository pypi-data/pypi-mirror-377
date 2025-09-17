import os
import base64
import uuid
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
        """Always True in this minimal version."""
        return True

    def _session_key(self, key: str) -> str:
        return f"{self.prefix}_{key}_cache"

    def get(self, key: str, default=None):
        """Retrieve a cookie (with session_state cache)."""
        # 1. If cached in session_state, return it
        cache_key = self._session_key(key)
        if cache_key in st.session_state:
            return st.session_state[cache_key]

        # 2. Otherwise call component
        unique_key = f"get_{key}_{uuid.uuid4().hex}"
        cookies = _cookie_component(action="get", key=unique_key) or {}
        enc_val = cookies.get(self.prefix + "_" + key)
        if not enc_val:
            st.session_state[cache_key] = default
            return default
        try:
            value = self.fernet.decrypt(enc_val.encode()).decode()
            st.session_state[cache_key] = value
            return value
        except InvalidToken:
            st.session_state[cache_key] = default
            return default

    def set(self, key: str, value: str):
        """Set a cookie and update cache."""
        enc_val = self.fernet.encrypt(value.encode()).decode()
        unique_key = f"set_{key}_{uuid.uuid4().hex}"
        _cookie_component(
            action="set",
            name=self.prefix + "_" + key,
            value=enc_val,
            key=unique_key
        )
        st.session_state[self._session_key(key)] = value

    def delete(self, key: str):
        """Delete a cookie and clear cache."""
        unique_key = f"del_{key}_{uuid.uuid4().hex}"
        _cookie_component(
            action="delete",
            name=self.prefix + "_" + key,
            key=unique_key
        )
        cache_key = self._session_key(key)
        if cache_key in st.session_state:
            del st.session_state[cache_key]

    def save(self):
        """Trigger cookie persistence (no-op in minimal version)."""
        unique_key = f"save_{uuid.uuid4().hex}"
        _cookie_component(action="save", key=unique_key)

    # --- Dict-style access ---
    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: str):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.delete(key)