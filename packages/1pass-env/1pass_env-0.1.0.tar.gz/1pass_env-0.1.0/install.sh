#!/usr/bin/env bash
# Installation and setup script for 1pass-env

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_header() {
    echo -e "${BLUE}🔐 1pass-env Installation Script${NC}"
    echo "======================================"
    echo
}

check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $python_version found"
    
    # Check if version is 3.8 or higher
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.8 or higher is required. Found: $python_version"
        exit 1
    fi
}

install_package() {
    print_info "Installing 1pass-env..."
    
    if pip3 install 1pass-env; then
        print_status "1pass-env installed successfully"
    else
        print_error "Failed to install 1pass-env"
        exit 1
    fi
}

check_service_account() {
    print_info "Checking 1Password service account configuration..."
    
    if [[ -z "${OP_SERVICE_ACCOUNT_TOKEN}" ]]; then
        print_warning "OP_SERVICE_ACCOUNT_TOKEN is not set"
        echo
        echo "To use 1Password integration, you need to:"
        echo "1. Create a service account at: https://my.1password.com/developer-tools/infrastructure-secrets/serviceaccount"
        echo "2. Export the token:"
        echo "   export OP_SERVICE_ACCOUNT_TOKEN='your-token-here'"
        echo
        echo "You can still use 1pass-env for regular environment variables without this token."
        return 1
    else
        print_status "OP_SERVICE_ACCOUNT_TOKEN is configured"
        return 0
    fi
}

test_installation() {
    print_info "Testing installation..."
    
    if command -v 1pass-env &> /dev/null; then
        version=$(1pass-env --version 2>&1 | head -1)
        print_status "1pass-env is installed: $version"
        
        # Test 1Password connectivity if token is available
        if check_service_account; then
            print_info "Testing 1Password connectivity..."
            if 1pass-env check; then
                print_status "1Password integration is working"
            else
                print_warning "1Password integration test failed"
            fi
        fi
    else
        print_error "1pass-env command not found after installation"
        exit 1
    fi
}

show_next_steps() {
    echo
    print_status "Installation complete!"
    echo
    echo "Next steps:"
    echo "1. Set up your 1Password service account token (if not already done):"
    echo "   export OP_SERVICE_ACCOUNT_TOKEN='your-token-here'"
    echo
    echo "2. Initialize your environment:"
    echo "   1pass-env init --create"
    echo
    echo "3. Set some variables:"
    echo "   1pass-env set DATABASE_URL 'postgresql://localhost/myapp'"
    echo "   1pass-env set API_KEY 'secret-key' --secure --vault 'My Vault'"
    echo
    echo "4. List your variables:"
    echo "   1pass-env list"
    echo
    echo "5. Run a command with your environment:"
    echo "   1pass-env run your-command"
    echo
    echo "For more help:"
    echo "   1pass-env --help"
    echo "   1pass-env check  # Test 1Password configuration"
    echo
}

main() {
    print_header
    
    check_python
    install_package
    test_installation
    show_next_steps
    
    print_status "All done! 🎉"
}

# Run main function
main
