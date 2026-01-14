"""
Admin Settings Page
Requires admin token to access - for managing API usage and other admin functions
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import get_connection, DATABASE_URL
from auth import AuthManager

# Page config
st.set_page_config(
    page_title="Admin Settings",
    page_icon="⚙️",
    layout="wide"
)

# ============================================================================
# ADMIN AUTHENTICATION CHECK
# ============================================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.error("🔒 **Access Denied** - You must be logged in to access this page")
    st.info("👉 Please return to the login page")
    st.stop()

# Check if user is admin
auth = AuthManager()
if 'auth_token' not in st.session_state or not auth.is_admin(st.session_state.auth_token):
    st.error("⛔ **Admin Access Required**")
    st.warning("This page is only accessible to administrators.")
    st.info("You are logged in as a regular user. Contact your administrator for admin access.")
    st.stop()

# ============================================================================
# END AUTHENTICATION CHECK
# ============================================================================

st.markdown("# ⚙️ Admin Settings")
st.markdown("---")

# Tabs for different admin functions
tab1, tab2 = st.tabs(["📊 API Usage Management", "🔐 Token Management"])

# ============================================================================
# TAB 1: API USAGE MANAGEMENT
# ============================================================================
with tab1:
    st.markdown("## 📊 API Usage Management")
    st.markdown("Manually adjust API usage tracking (useful after server restarts or migrations)")
    
    # Get current usage
    current_month = datetime.now().strftime("%Y-%m")
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if DATABASE_URL:
            cursor.execute("SELECT * FROM api_usage WHERE month = %s", (current_month,))
        else:
            cursor.execute("SELECT * FROM api_usage WHERE month = ?", (current_month,))
        
        result = cursor.fetchone()
        
        if result:
            usage_data = dict(result)
            
            # Display current usage
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Month", usage_data["month"])
            with col2:
                st.metric("Requests Made", usage_data["requests_made"])
            with col3:
                st.metric("Monthly Limit", usage_data["monthly_limit"])
            
            st.markdown("---")
            
            # Form to update usage
            with st.form("update_usage_form"):
                st.markdown("### Update Usage")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_requests = st.number_input(
                        "Requests Made",
                        min_value=0,
                        value=usage_data["requests_made"],
                        help="Set the current number of API requests used this month"
                    )
                
                with col2:
                    new_limit = st.number_input(
                        "Monthly Limit",
                        min_value=1,
                        value=usage_data["monthly_limit"],
                        help="Set the maximum number of API requests allowed per month"
                    )
                
                submitted = st.form_submit_button("💾 Update Usage", use_container_width=True)
                
                if submitted:
                    try:
                        if DATABASE_URL:
                            cursor.execute(
                                """UPDATE api_usage 
                                   SET requests_made = %s, monthly_limit = %s
                                   WHERE month = %s""",
                                (new_requests, new_limit, current_month)
                            )
                        else:
                            cursor.execute(
                                """UPDATE api_usage 
                                   SET requests_made = ?, monthly_limit = ?
                                   WHERE month = ?""",
                                (new_requests, new_limit, current_month)
                            )
                        conn.commit()
                        st.success(f"✅ Usage updated! Requests: {new_requests}, Limit: {new_limit}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating usage: {str(e)}")
        else:
            st.warning(f"⚠️ No usage data found for {current_month}")
            st.info("The system will automatically create a usage record when API requests are made.")
            
            # Option to manually create usage record
            with st.form("create_usage_form"):
                st.markdown("### Initialize Usage for Current Month")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    initial_requests = st.number_input(
                        "Initial Requests Made",
                        min_value=0,
                        value=0,
                        help="Set the starting number of requests for this month"
                    )
                
                with col2:
                    initial_limit = st.number_input(
                        "Monthly Limit",
                        min_value=1,
                        value=1000,
                        help="Set the maximum number of API requests allowed per month"
                    )
                
                create_submitted = st.form_submit_button("🆕 Create Usage Record", use_container_width=True)
                
                if create_submitted:
                    try:
                        if DATABASE_URL:
                            cursor.execute(
                                """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                                   VALUES (%s, %s, %s, %s)""",
                                (current_month, initial_requests, initial_limit, datetime.now())
                            )
                        else:
                            cursor.execute(
                                """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                                   VALUES (?, ?, ?, ?)""",
                                (current_month, initial_requests, initial_limit, datetime.now())
                            )
                        conn.commit()
                        st.success(f"✅ Usage record created for {current_month}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating usage record: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TAB 2: TOKEN MANAGEMENT
# ============================================================================
with tab2:
    st.markdown("## 🔐 Token Management")
    st.markdown("View and manage authentication tokens")
    
    tokens = auth.list_all_tokens()
    
    if tokens:
        st.markdown(f"**Total Tokens:** {len(tokens)}")
        
        for token_data in tokens:
            with st.expander(f"👤 {token_data['username']} {'🔑 (Admin)' if token_data.get('is_admin', False) else ''}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.text(f"Token: {token_data['token'][:32]}...")
                    st.text(f"Created: {token_data['created_at']}")
                    st.text(f"Last Used: {token_data.get('last_used', 'Never')}")
                    st.text(f"Status: {'🟢 Active' if token_data['active'] else '🔴 Inactive'}")
                    st.text(f"Admin: {'✅ Yes' if token_data.get('is_admin', False) else '❌ No'}")
                
                with col2:
                    if token_data['active'] and not token_data.get('is_admin', False):
                        if st.button(f"🚫 Revoke", key=f"revoke_{token_data['token'][:16]}"):
                            auth.revoke_token(token_data['token'])
                            st.success("Token revoked!")
                            st.rerun()
    else:
        st.info("No tokens found")

st.markdown("---")
st.markdown("*⚠️ Be careful when modifying these settings. Incorrect values may affect system functionality.*")
