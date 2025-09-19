#!/usr/bin/env python3
"""
Setup script for 1pass-env.
This script helps users get started with 1pass-env by guiding them through the setup process.
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print the setup header."""
    print("🔐 1pass-env Setup")
    print("=" * 40)
    print()

def check_service_account_token():
    """Check if OP_SERVICE_ACCOUNT_TOKEN is set."""
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        print("❌ OP_SERVICE_ACCOUNT_TOKEN is not set")
        print()
        print("To fix this:")
        print("1. Go to https://my.1password.com/developer-tools/infrastructure-secrets/serviceaccount")
        print("2. Create a new service account")
        print("3. Copy the token and run:")
        print("   export OP_SERVICE_ACCOUNT_TOKEN='your-token-here'")
        print()
        print("Then run this setup script again.")
        return False
    
    print("✅ OP_SERVICE_ACCOUNT_TOKEN is configured")
    return True

def test_1password_connection():
    """Test connection to 1Password."""
    try:
        from onepass_env.onepassword import OnePasswordClient
        
        print("🔄 Testing 1Password connection...")
        client = OnePasswordClient()
        
        if not client.is_authenticated():
            print("❌ Failed to authenticate with 1Password")
            print("Please check your service account token.")
            return False
        
        print("✅ Successfully connected to 1Password")
        
        # List available vaults
        print("\n📁 Available vaults:")
        op_client = client._get_client()
        vaults = op_client.vaults.list_all()
        
        if not vaults:
            print("   No vaults found")
        else:
            for vault in vaults:
                print(f"   • {vault.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to 1Password: {e}")
        return False

def create_sample_env():
    """Create a sample .env file."""
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"📄 .env file already exists")
        return
    
    response = input("📄 Create a sample .env file? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        sample_content = """# Sample .env file created by 1pass-env
# Regular environment variables
DATABASE_URL=postgresql://localhost:5432/myapp
DEBUG=true
PORT=3000

# Secure variables will be stored in 1Password when you use --secure flag
# Example: 1pass-env set API_KEY "your-secret-key" --secure
"""
        
        env_file.write_text(sample_content)
        print("✅ Created sample .env file")
    else:
        print("⏭️  Skipped .env file creation")

def show_next_steps():
    """Show next steps to the user."""
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Set a regular variable:")
    print("   1pass-env set MY_VAR 'my-value'")
    print()
    print("2. Set a secure variable (stored in 1Password):")
    print("   1pass-env set SECRET_KEY 'super-secret' --secure --vault 'Your-Vault'")
    print()
    print("3. List all variables:")
    print("   1pass-env list")
    print()
    print("4. Run a command with variables loaded:")
    print("   1pass-env run your-command")
    print()
    print("For more help, run: 1pass-env --help")

def main():
    """Main setup function."""
    print_header()
    
    # Check if 1pass-env is installed
    try:
        import onepass_env
        print(f"✅ 1pass-env {onepass_env.__version__} is installed")
    except ImportError:
        print("❌ 1pass-env is not installed")
        print("Install it with: pip install 1pass-env")
        sys.exit(1)
    
    print()
    
    # Check service account token
    if not check_service_account_token():
        sys.exit(1)
    
    print()
    
    # Test 1Password connection
    if not test_1password_connection():
        sys.exit(1)
    
    print()
    
    # Create sample .env file
    create_sample_env()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
