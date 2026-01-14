"""
Database Diagnostic Page
Shows what's actually in the Render PostgreSQL database
Access this page without authentication to diagnose token issues
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import get_connection, DATABASE_URL, init_db
from datetime import datetime

st.set_page_config(
    page_title="Database Diagnostic",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Database Diagnostic Tool")

# Show database type
if DATABASE_URL:
    st.success("🌐 Connected to: **PostgreSQL (Render Production)**")
    st.info(f"Database URL: {DATABASE_URL[:30]}...{DATABASE_URL[-20:] if len(DATABASE_URL) > 50 else ''}")
else:
    st.warning("💻 Connected to: **SQLite (Local Development)**")

st.markdown("---")

# Add manual fix button at the top
st.header("🚨 Emergency Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Run Token Fix Now", type="primary", use_container_width=True):
        with st.spinner("Fixing tokens..."):
            try:
                from force_fix_tokens import emergency_token_fix
                success = emergency_token_fix()
                if success:
                    st.success("✅ Tokens fixed successfully!")
                    st.balloons()
                else:
                    st.error("❌ Token fix failed. Check logs below.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.code(str(e))

with col2:
    if st.button("🔄 Initialize Database Schema", use_container_width=True):
        with st.spinner("Initializing database..."):
            try:
                init_db()
                st.success("✅ Database schema initialized!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")

# Check auth_tokens table
st.header("🔑 Authentication Tokens")

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if table exists
    if DATABASE_URL:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'auth_tokens'
            )
        """)
        result = cursor.fetchone()
        table_exists = list(result.values())[0] if result else False
    else:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='auth_tokens'
        """)
        table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        st.error("❌ auth_tokens table does NOT exist!")
        st.warning("Click 'Initialize Database Schema' button above to create it.")
    else:
        st.success("✅ auth_tokens table exists")
        
        # Get token countas count FROM auth_tokens")
        result = cursor.fetchone()
        count = result['count'] if DATABASE_URL else resultUNT(*) FROM auth_tokens")
        count = cursor.fetchone()[0]
        
        st.metric("Total Tokens", count)
        
        if count == 0:
            st.warning("⚠️ No tokens found in database!")
            st.info("Click 'Run Token Fix Now' button above to insert tokens.")
        else:
            # Show all tokens
            cursor.execute("""
                SELECT token, username, active, is_admin, created_at, last_used 
                FROM auth_tokens 
                ORDER BY is_admin DESC, username
            """)
            results = cursor.fetchall()
            
            st.subheader(f"Found {len(results)} tokens:")
            
            for row in results:
                row_dict = dict(row)
                
                # Create expandable section for each token
                with st.expander(
                    f"{'🔑 ADMIN' if row_dict['is_admin'] else '👤 USER'} - {row_dict['username']} "
                    f"({'🟢 Active' if row_dict['active'] else '🔴 Inactive'})"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Username:**", row_dict['username'])
                        st.write("**Role:**", "🔑 Admin" if row_dict['is_admin'] else "👤 User")
                        st.write("**Status:**", "🟢 Active" if row_dict['active'] else "🔴 Inactive")
                    
                    with col2:
                        st.write("**Created:**", row_dict.get('created_at', 'N/A'))
                        st.write("**Last Used:**", row_dict.get('last_used', 'Never'))
                    
                    # Show full token
                    token = row_dict['token']
                    st.code(token, language=None)
                    
                    # Test token
                    if st.button(f"Test {row_dict['username']}", key=f"test_{token[:16]}"):
                        from auth import AuthManager
                        auth = AuthManager()
                        is_valid = auth.validate_token(token)
                        if is_valid:
                            st.success(f"✅ Token is VALID and working!")
                        else:
                            st.error(f"❌ Token validation FAILED!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    st.error(f"❌ Error accessing database: {e}")
    st.code(str(e))
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")

# Check api_usage table
st.header("📊 API Usage")

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM api_usage ORDER BY month DESC LIMIT 5")
    results = cursor.fetchall()
    
    if len(results) == 0:
        st.info("No API usage data found")
    else:
        for row in results:
            row_dict = dict(row)
            st.write(f"**Month:** {row_dict.get('month', 'N/A')}")
            st.write(f"**Requests:** {row_dict.get('requests_made', 0)} / {row_dict.get('monthly_limit', 0)}")
            st.markdown("---")
    
    cursor.close()
    conn.close()
    
except Exception as  accessing API usage: {e}")
    import traceback
    st.code(traceback.format_exc()
    st.error(f"Error: {e}")

st.markdown("---")

# Check leads table
st.header("📋 Leads")

try:
    conn = get_connection()
    cursor = conn.cursor()as count FROM leads")
    result = cursor.fetchone()
    count = result['count'] if DATABASE_URL else result[0]
    
    st.metric("Total Leads", count)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    st.error(f"Error accessing leads: {e}")
    import traceback
    st.code(traceback.format_exc()
except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")

# Show environment info
st.header("🔧 Environment Information")

import os

env_vars = {
    "DATABASE_URL": "✅ Set" if DATABASE_URL else "❌ Not Set",
    "GOOGLE_MAPS_API_KEY": "✅ Set" if os.getenv('GOOGLE_MAPS_API_KEY') else "❌ Not Set",
    "MONTHLY_API_LIMIT": os.getenv('MONTHLY_API_LIMIT', 'Not Set'),
    "MASTER_AUTH_TOKEN": "✅ Set" if os.getenv('MASTER_AUTH_TOKEN') else "❌ Not Set",
}

for key, value in env_vars.items():
    st.write(f"**{key}:** {value}")

st.markdown("---")
st.caption("Last refreshed: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.caption("Refresh page to update data")
