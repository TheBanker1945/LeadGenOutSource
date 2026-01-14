"""
Authentication system for Lead Generation Dashboard
Token-based authentication - no registration required
"""

import json
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class AuthManager:
    """Manages authentication tokens for the dashboard."""
    
    def __init__(self, tokens_file: str = "auth_tokens.json"):
        """
        Initialize the auth manager.
        
        Args:
            tokens_file: Path to the JSON file storing auth tokens
        """
        self.tokens_file = Path(tokens_file)
        self._ensure_tokens_file()
    
    def _ensure_tokens_file(self):
        """Create tokens file if it doesn't exist."""
        if not self.tokens_file.exists():
            self._save_tokens({})
    
    def _load_tokens(self) -> Dict:
        """Load tokens from JSON file."""
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_tokens(self, tokens: Dict):
        """Save tokens to JSON file."""
        with open(self.tokens_file, 'w') as f:
            json.dump(tokens, f, indent=4, default=str)
    
    def generate_token(self, username: str = None) -> str:
        """
        Generate a new authentication token.
        
        Args:
            username: Optional username/label for the token
            
        Returns:
            Generated authentication token
        """
        # Generate a secure random token (32 bytes = 64 hex characters)
        token = secrets.token_hex(32)
        
        # Load existing tokens
        tokens = self._load_tokens()
        
        # Store token with metadata
        tokens[token] = {
            "username": username or f"user_{len(tokens) + 1}",
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "active": True
        }
        
        # Save tokens
        self._save_tokens(tokens)
        
        return token
    
    def validate_token(self, token: str) -> bool:
        """
        Validate an authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid and active, False otherwise
        """
        tokens = self._load_tokens()
        
        if token not in tokens:
            return False
        
        token_data = tokens[token]
        
        # Check if token is active
        if not token_data.get("active", False):
            return False
        
        # Update last used timestamp
        token_data["last_used"] = datetime.now().isoformat()
        tokens[token] = token_data
        self._save_tokens(tokens)
        
        return True
    
    def get_token_info(self, token: str) -> Optional[Dict]:
        """
        Get information about a token.
        
        Args:
            token: Token to get info for
            
        Returns:
            Token metadata or None if token doesn't exist
        """
        tokens = self._load_tokens()
        return tokens.get(token)
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke/deactivate a token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if token was revoked, False if token doesn't exist
        """
        tokens = self._load_tokens()
        
        if token not in tokens:
            return False
        
        tokens[token]["active"] = False
        self._save_tokens(tokens)
        return True
    
    def list_all_tokens(self) -> List[Dict]:
        """
        List all tokens with their metadata.
        
        Returns:
            List of token dictionaries with token and metadata
        """
        tokens = self._load_tokens()
        return [
            {
                "token": token,
                **data
            }
            for token, data in tokens.items()
        ]


def generate_initial_tokens(count: int = 3) -> List[str]:
    """
    Generate initial authentication tokens for setup.
    
    Args:
        count: Number of tokens to generate
        
    Returns:
        List of generated tokens
    """
    auth = AuthManager()
    tokens = []
    
    print("=" * 80)
    print("🔐 AUTHENTICATION TOKENS GENERATED")
    print("=" * 80)
    print("\nSave these tokens securely! They provide access to your dashboard.\n")
    
    for i in range(count):
        token = auth.generate_token(f"user_{i + 1}")
        tokens.append(token)
        print(f"Token {i + 1}: {token}")
    
    print("\n" + "=" * 80)
    print(f"✅ {count} tokens generated and saved to auth_tokens.json")
    print("=" * 80)
    
    return tokens


if __name__ == "__main__":
    # Generate 3 initial tokens when run directly
    generate_initial_tokens(3)
