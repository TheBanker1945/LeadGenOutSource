"""
Password Hash Generator for Streamlit Authentication
Run this script to generate hashed passwords for your clients.
"""

import streamlit_authenticator as stauth

def generate_password_hash(password: str) -> str:
    """Generate a bcrypt hash for the given password."""
    return stauth.Hasher([password]).generate()[0]

if __name__ == "__main__":
    print("=" * 60)
    print("Streamlit Password Hash Generator")
    print("=" * 60)
    print()
    
    while True:
        password = input("Enter password to hash (or 'quit' to exit): ").strip()
        
        if password.lower() == 'quit':
            print("\nGoodbye!")
            break
        
        if len(password) < 8:
            print("⚠️  Warning: Password is too short (minimum 8 characters recommended)")
            continue
        
        hashed = generate_password_hash(password)
        
        print(f"\n✅ Hashed password:")
        print(f"   {hashed}")
        print()
        print(f"Add this to your Streamlit secrets:")
        print(f"   [credentials.usernames.client1]")
        print(f"   name = \"Client Name\"")
        print(f"   password = \"{hashed}\"")
        print()
        print("-" * 60)
        print()
