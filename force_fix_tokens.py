"""
EMERGENCY TOKEN FIX SCRIPT
Run this script to force-fix all authentication tokens in the database.
This script can be run via the Render web service or shell.

This will:
1. Connect to the database
2. Delete ALL existing tokens
3. Insert all 4 tokens with correct permissions
4. Verify all tokens are active and accessible
"""

import os
from datetime import datetime
from src.database.db_manager import get_connection, DATABASE_URL, init_db

def emergency_token_fix():
    """Emergency fix for all authentication tokens."""
    print("=" * 80)
    print("🚨 EMERGENCY TOKEN FIX")
    print("=" * 80)
    
    # Initialize database schema first
    print("\n1️⃣ Initializing database schema...")
    try:
        init_db()
        print("   ✅ Database schema ready")
    except Exception as e:
        print(f"   ⚠️  Schema initialization warning: {e}")
    
    # Determine which database we're using
    if DATABASE_URL:
        print(f"\n🌐 Database: PostgreSQL (Render Production)")
    else:
        print(f"\n💻 Database: SQLite (Local Development)")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Delete all existing tokens
        print("\n2️⃣ Clearing existing tokens...")
        if DATABASE_URL:
            cursor.execute("DELETE FROM auth_tokens")
        else:
            cursor.execute("DELETE FROM auth_tokens")
        conn.commit()
        print("   ✅ All old tokens cleared")
        
        # Step 2: Define correct tokens
        correct_tokens = [
            {
                "token": "a9f8c2d4e1b7a5f3c8d6e2b9a7f4c1d8e5b3a6f9c2d7e4b1a8f5c3d9e6b2a7f4",
                "username": "admin",
                "is_admin": True,
                "description": "Primary admin token"
            },
            {
                "token": "e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474",
                "username": "user_1",
                "is_admin": True,
                "description": "Secondary admin token"
            },
            {
                "token": "b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407",
                "username": "user_2",
                "is_admin": False,
                "description": "Regular user token"
            },
            {
                "token": "5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5",
                "username": "user_3",
                "is_admin": False,
                "description": "Regular user token"
            }
        ]
        
        # Step 3: Insert all tokens
        print("\n3️⃣ Inserting correct tokens...")
        for token_data in correct_tokens:
            if DATABASE_URL:
                # PostgreSQL
                cursor.execute("""
                    INSERT INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    token_data['token'],
                    token_data['username'],
                    datetime.now(),
                    None,
                    True,
                    token_data['is_admin']
                ))
            else:
                # SQLite
                cursor.execute("""
                    INSERT INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    token_data['token'],
                    token_data['username'],
                    datetime.now().isoformat(),
                    None,
                    True,
                    token_data['is_admin']
                ))
            
            role_emoji = "🔑" if token_data['is_admin'] else "👤"
            print(f"   ✅ {token_data['username']}: {role_emoji} {token_data['description']}")
        
        conn.commit()
        print("   ✅ All tokens inserted successfully")
        
        # Step 4: Verify tokens
        print("\n4️⃣ Verification:")
        if DATABASE_URL:
            cursor.execute("SELECT token, username, is_admin, active FROM auth_tokens ORDER BY is_admin DESC, username")
        else:
            cursor.execute("SELECT token, username, is_admin, active FROM auth_tokens ORDER BY is_admin DESC, username")
        
        results = cursor.fetchall()
        
        if len(results) == 0:
            print("   ❌ ERROR: No tokens found after insertion!")
            return False
        
        print(f"   Found {len(results)} tokens in database:")
        for row in results:
            row_dict = dict(row)
            role = "🔑 Admin" if row_dict['is_admin'] else "👤 User"
            status = "🟢 Active" if row_dict['active'] else "🔴 Inactive"
            token_preview = row_dict['token'][:16] + "..." + row_dict['token'][-16:]
            print(f"   • {row_dict['username']}: {role} {status}")
            print(f"     Token: {token_preview}")
        
        # Step 5: Test authentication
        print("\n5️⃣ Testing authentication...")
        from auth import AuthManager
        auth = AuthManager()
        
        all_valid = True
        for token_data in correct_tokens:
            is_valid = auth.validate_token(token_data['token'])
            status = "✅" if is_valid else "❌"
            print(f"   {status} {token_data['username']}: {'VALID' if is_valid else 'INVALID'}")
            if not is_valid:
                all_valid = False
        
        if all_valid:
            print("\n" + "=" * 80)
            print("✅ ALL TOKENS FIXED AND VERIFIED!")
            print("=" * 80)
            print("\n🎉 You can now login with any of these 4 tokens:")
            for token_data in correct_tokens:
                role = "ADMIN" if token_data['is_admin'] else "USER"
                print(f"\n   {token_data['username']} ({role}):")
                print(f"   {token_data['token']}")
            print("\n" + "=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("⚠️  TOKENS INSERTED BUT VALIDATION FAILED")
            print("=" * 80)
            print("\n   Tokens are in database but authentication test failed.")
            print("   Try restarting the application.")
            print("=" * 80)
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = emergency_token_fix()
    exit(0 if success else 1)
