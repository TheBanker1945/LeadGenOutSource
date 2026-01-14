"""
Login page for Lead Generation Dashboard
Token-based authentication
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from auth import AuthManager

# Page config
st.set_page_config(
    page_title="Login - Lead Generation Dashboard",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS for login page
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .login-container {
        background-color: white;
        padding: 3rem;
        border-radius: 1rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        max-width: 500px;
        margin: 4rem auto;
    }
    .login-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #764ba2;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .stTextInput > div > div > input {
        font-size: 1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .icon-container {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize auth manager
auth = AuthManager()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

def login(token: str):
    """Handle login attempt."""
    if auth.validate_token(token):
        st.session_state.authenticated = True
        st.session_state.auth_token = token
        token_info = auth.get_token_info(token)
        st.session_state.username = token_info.get('username', 'User')
        return True
    return False

# Main login interface
st.markdown('<div class="icon-container">🔐</div>', unsafe_allow_html=True)
st.markdown('<div class="login-header">Lead Generation Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subtitle">Enter your authentication token to continue</div>', unsafe_allow_html=True)

# Check if already authenticated
if st.session_state.authenticated:
    st.success(f"✅ Already authenticated as **{st.session_state.username}**")
    st.info("👉 The dashboard should open automatically. If not, use the navigation menu.")
    
    if st.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.session_state.auth_token = None
        st.session_state.username = None
        st.rerun()
    
    # Redirect to dashboard
    st.switch_page("dashboard.py")
else:
    # Login form
    with st.form("login_form", clear_on_submit=False):
        token_input = st.text_input(
            "Authentication Token",
            type="password",
            placeholder="Enter your 64-character authentication token",
            help="This token was provided to you by the system administrator",
            key="token_input"
        )
        
        submit_button = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submit_button:
            if not token_input:
                st.error("⚠️ Please enter an authentication token")
            elif len(token_input) != 64:
                st.error("⚠️ Invalid token format. Token must be 64 characters long.")
            else:
                with st.spinner("Authenticating..."):
                    if login(token_input):
                        st.success(f"✅ Login successful! Welcome, **{st.session_state.username}**")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid or inactive authentication token. Please check your token and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🔒 Secure token-based authentication</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">
        Don't have a token? Contact your system administrator.
    </p>
</div>
""", unsafe_allow_html=True)
