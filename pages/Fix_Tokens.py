"""
Simple web-accessible token fix endpoint
Visit /fix_tokens_now in your browser to trigger the fix
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Fix Tokens",
    page_icon="🔧",
    layout="centered"
)

st.title("🔧 Emergency Token Fix")

st.warning("""
⚠️ **Warning:** This will delete ALL existing tokens and recreate them.
Only use this if you're experiencing login issues.
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 FIX TOKENS NOW", type="primary", use_container_width=True):
        
        st.markdown("### 📋 Fix Progress:")
        progress_placeholder = st.empty()
        log_placeholder = st.empty()
        
        log_messages = []
        
        try:
            # Import and run the fix
            import io
            import contextlib
            from force_fix_tokens import emergency_token_fix
            
            # Capture output
            output_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(output_buffer):
                success = emergency_token_fix()
            
            # Show output
            output = output_buffer.getvalue()
            st.code(output)
            
            if success:
                st.success("✅ **ALL TOKENS FIXED SUCCESSFULLY!**")
                st.balloons()
                
                st.markdown("---")
                st.markdown("### 🎉 You can now login with these tokens:")
                
                tokens = [
                    ("a9f8c2d4e1b7a5f3c8d6e2b9a7f4c1d8e5b3a6f9c2d7e4b1a8f5c3d9e6b2a7f4", "admin", "🔑 ADMIN"),
                    ("e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474", "user_1", "🔑 ADMIN"),
                    ("b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407", "user_2", "👤 USER"),
                    ("5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5", "user_3", "👤 USER"),
                ]
                
                for token, username, role in tokens:
                    with st.expander(f"{role} - {username}"):
                        st.code(token, language=None)
                
                st.info("👉 Go to the login page and use any of these tokens!")
                
            else:
                st.error("❌ **Token fix failed!**")
                st.warning("Check the output above for errors.")
                
        except Exception as e:
            st.error(f"❌ **Error:** {e}")
            st.code(str(e))
            
            import traceback
            st.code(traceback.format_exc())

with col2:
    if st.button("📊 View Database Status", use_container_width=True):
        st.info("Redirecting to Database Diagnostic page...")
        st.switch_page("pages/Database_Diagnostic.py")

st.markdown("---")

st.info("""
### What this does:
1. Connects to your Render PostgreSQL database
2. Deletes all existing authentication tokens
3. Creates 4 new tokens:
   - **admin** (🔑 Admin)
   - **user_1** (🔑 Admin) 
   - **user_2** (👤 User)
   - **user_3** (👤 User)
4. Verifies all tokens work correctly
""")

st.markdown("---")
st.caption("Database Diagnostic & Token Fix Tool")
