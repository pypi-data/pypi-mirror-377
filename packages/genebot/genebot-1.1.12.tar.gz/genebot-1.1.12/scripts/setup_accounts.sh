#!/bin/bash
# Account Setup Script for Trading Bot
# This script helps users set up their exchange and broker accounts

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT="$SCRIPT_DIR/trading_bot_cli.py"

print_header() {
    echo -e "${CYAN}${1}${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..60})${NC}"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

# Function to validate input
validate_not_empty() {
    local value="$1"
    local field_name="$2"
    
    if [[ -z "$value" ]]; then
        print_error "$field_name cannot be empty"
        return 1
    fi
    return 0
}

# Function to check for placeholder values
check_placeholder() {
    local value="$1"
    local field_name="$2"
    
    local placeholders=("your_" "placeholder" "example" "demo_" "test_" "sample_")
    
    for placeholder in "${placeholders[@]}"; do
        if [[ "$value" == *"$placeholder"* ]]; then
            print_warning "$field_name appears to contain placeholder text: $value"
            echo -n "Continue anyway? [y/N]: "
            read -r continue_choice
            if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
                return 1
            fi
            break
        fi
    done
    return 0
}

# Function to setup crypto exchange
setup_crypto_exchange() {
    print_header "Setup Crypto Exchange Account"
    
    echo "Available exchanges:"
    echo "1. Binance"
    echo "2. Coinbase"
    echo "3. Kraken"
    echo "4. KuCoin"
    echo "5. Bybit"
    echo
    
    read -p "Select exchange (1-5): " exchange_choice
    
    case "$exchange_choice" in
        1) exchange_type="binance" ;;
        2) exchange_type="coinbase" ;;
        3) exchange_type="kraken" ;;
        4) exchange_type="kucoin" ;;
        5) exchange_type="bybit" ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    echo
    print_info "Setting up $exchange_type account"
    echo
    
    # Get account details
    read -p "Account name (e.g., ${exchange_type}-main): " account_name
    validate_not_empty "$account_name" "Account name" || return 1
    
    echo
    print_warning "API Credentials (will be hidden when typing)"
    read -s -p "API Key: " api_key
    echo
    validate_not_empty "$api_key" "API Key" || return 1
    check_placeholder "$api_key" "API Key" || return 1
    
    read -s -p "API Secret: " api_secret
    echo
    validate_not_empty "$api_secret" "API Secret" || return 1
    check_placeholder "$api_secret" "API Secret" || return 1
    
    # API Passphrase for Coinbase
    api_passphrase=""
    if [[ "$exchange_type" == "coinbase" ]]; then
        read -s -p "API Passphrase (required for Coinbase): " api_passphrase
        echo
        validate_not_empty "$api_passphrase" "API Passphrase" || return 1
    fi
    
    echo
    echo "Trading Mode:"
    echo "1. Sandbox/Testnet (recommended for testing)"
    echo "2. Live Trading (real money)"
    read -p "Select mode (1-2): " mode_choice
    
    case "$mode_choice" in
        1) sandbox_mode="--sandbox" ;;
        2) sandbox_mode="" ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    # Optional settings
    echo
    read -p "Rate limit per minute [1200]: " rate_limit
    rate_limit=${rate_limit:-1200}
    
    read -p "Request timeout in seconds [30]: " timeout
    timeout=${timeout:-30}
    
    # Build command
    local cmd_args=(
        "add-crypto"
        "--name" "$account_name"
        "--exchange-type" "$exchange_type"
        "--api-key" "$api_key"
        "--api-secret" "$api_secret"
        "--rate-limit" "$rate_limit"
        "--timeout" "$timeout"
        "--enabled"
        "--force"
    )
    
    if [[ -n "$api_passphrase" ]]; then
        cmd_args+=("--api-passphrase" "$api_passphrase")
    fi
    
    if [[ -n "$sandbox_mode" ]]; then
        cmd_args+=("$sandbox_mode")
    fi
    
    # Execute command
    echo
    print_info "Adding $exchange_type account..."
    if python "$CLI_SCRIPT" "${cmd_args[@]}"; then
        print_success "$exchange_type account added successfully!"
        
        if [[ -n "$sandbox_mode" ]]; then
            print_warning "Account is configured for sandbox/testnet mode"
            print_info "Switch to live trading when you're ready by editing the configuration"
        fi
    else
        print_error "Failed to add $exchange_type account"
        return 1
    fi
}

# Function to setup forex broker
setup_forex_broker() {
    print_header "Setup Forex Broker Account"
    
    echo "Available brokers:"
    echo "1. OANDA"
    echo "2. MetaTrader 5 (MT5)"
    echo "3. Interactive Brokers"
    echo
    
    read -p "Select broker (1-3): " broker_choice
    
    case "$broker_choice" in
        1) broker_type="oanda" ;;
        2) broker_type="mt5" ;;
        3) broker_type="interactive_brokers" ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    echo
    print_info "Setting up $broker_type account"
    echo
    
    # Get account name
    read -p "Account name (e.g., ${broker_type}-main): " account_name
    validate_not_empty "$account_name" "Account name" || return 1
    
    # Broker-specific setup
    local cmd_args=(
        "add-forex"
        "--name" "$account_name"
        "--broker-type" "$broker_type"
        "--enabled"
        "--force"
    )
    
    case "$broker_type" in
        "oanda")
            echo
            print_warning "OANDA Credentials (will be hidden when typing)"
            read -s -p "API Key: " api_key
            echo
            validate_not_empty "$api_key" "API Key" || return 1
            check_placeholder "$api_key" "API Key" || return 1
            
            read -p "Account ID (e.g., 101-001-12345678-001): " account_id
            validate_not_empty "$account_id" "Account ID" || return 1
            
            cmd_args+=("--api-key" "$api_key" "--account-id" "$account_id")
            ;;
            
        "mt5")
            echo
            print_warning "MetaTrader 5 Credentials"
            read -p "Server (e.g., Demo-Server): " server
            validate_not_empty "$server" "Server" || return 1
            
            read -p "Login: " login
            validate_not_empty "$login" "Login" || return 1
            
            read -s -p "Password: " password
            echo
            validate_not_empty "$password" "Password" || return 1
            
            cmd_args+=("--server" "$server" "--login" "$login" "--password" "$password")
            ;;
            
        "interactive_brokers")
            echo
            print_info "Interactive Brokers Connection Settings"
            read -p "Host [127.0.0.1]: " host
            host=${host:-127.0.0.1}
            
            read -p "Port (7497 for paper, 7496 for live) [7497]: " port
            port=${port:-7497}
            
            read -p "Client ID [1]: " client_id
            client_id=${client_id:-1}
            
            cmd_args+=("--host" "$host" "--port" "$port" "--client-id" "$client_id")
            ;;
    esac
    
    # Trading mode
    echo
    echo "Trading Mode:"
    echo "1. Demo/Paper Trading (recommended for testing)"
    echo "2. Live Trading (real money)"
    read -p "Select mode (1-2): " mode_choice
    
    case "$mode_choice" in
        1) cmd_args+=("--sandbox") ;;
        2) ;; # No sandbox flag for live trading
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    # Execute command
    echo
    print_info "Adding $broker_type account..."
    if python "$CLI_SCRIPT" "${cmd_args[@]}"; then
        print_success "$broker_type account added successfully!"
        
        if [[ "$mode_choice" == "1" ]]; then
            print_warning "Account is configured for demo/paper trading mode"
            print_info "Switch to live trading when you're ready by editing the configuration"
        fi
    else
        print_error "Failed to add $broker_type account"
        return 1
    fi
}

# Function to setup environment file
setup_environment() {
    print_header "Setup Environment Configuration"
    
    local env_file=".env"
    
    if [[ -f "$env_file" ]]; then
        print_warning "Environment file already exists: $env_file"
        echo -n "Overwrite? [y/N]: "
        read -r overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            print_info "Keeping existing environment file"
            return 0
        fi
    fi
    
    cat > "$env_file" << 'EOF'
# Trading Bot Environment Configuration
# Copy this file to .env and customize with your settings

# Application Settings
APP_NAME="TradingBot"
APP_VERSION="2.0.0"
DEBUG=false
DRY_RUN=true
ENVIRONMENT=development

# Database Configuration
DATABASE_URL="sqlite:///trading_bot.db"

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE="logs/trading_bot.log"

# Risk Management
RISK_MAX_POSITION_SIZE=0.1
RISK_MAX_DAILY_LOSS=0.05
RISK_PER_TRADE=0.01

# Example Exchange API Keys (replace with your actual keys)
# BINANCE_API_KEY=your_binance_api_key_here
# BINANCE_API_SECRET=your_binance_api_secret_here

# COINBASE_API_KEY=your_coinbase_api_key_here
# COINBASE_API_SECRET=your_coinbase_api_secret_here
# COINBASE_PASSPHRASE=your_coinbase_passphrase_here

# OANDA_API_KEY=your_oanda_api_key_here
# OANDA_ACCOUNT_ID=your_oanda_account_id_here

# Security Note: Never commit this file to version control
# Add .env to your .gitignore file
EOF
    
    print_success "Environment file created: $env_file"
    print_warning "Remember to:"
    print_info "1. Add your actual API keys to the .env file"
    print_info "2. Add .env to your .gitignore file"
    print_info "3. Set appropriate file permissions: chmod 600 .env"
}

# Function to validate setup
validate_setup() {
    print_header "Validating Setup"
    
    # Check if accounts are configured
    if python "$CLI_SCRIPT" list-accounts | grep -q "No.*configured"; then
        print_warning "No accounts configured yet"
        return 1
    fi
    
    # Validate accounts
    if python "$CLI_SCRIPT" validate-accounts; then
        print_success "Account validation passed"
    else
        print_error "Account validation failed"
        return 1
    fi
    
    print_success "Setup validation completed!"
}

# Main menu
show_main_menu() {
    print_header "Trading Bot Account Setup"
    
    echo "What would you like to set up?"
    echo
    echo "1. Crypto Exchange Account"
    echo "2. Forex Broker Account"
    echo "3. Environment Configuration"
    echo "4. Validate Current Setup"
    echo "5. List Current Accounts"
    echo "6. Exit"
    echo
    
    read -p "Select option (1-6): " choice
    
    case "$choice" in
        1)
            setup_crypto_exchange
            ;;
        2)
            setup_forex_broker
            ;;
        3)
            setup_environment
            ;;
        4)
            validate_setup
            ;;
        5)
            python "$CLI_SCRIPT" list-accounts
            ;;
        6)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
}

# Main execution
main() {
    # Check if CLI script exists
    if [[ ! -f "$CLI_SCRIPT" ]]; then
        print_error "CLI script not found: $CLI_SCRIPT"
        exit 1
    fi
    
    # Check if running interactively
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        while true; do
            echo
            show_main_menu
            echo
            echo -n "Continue with another setup? [Y/n]: "
            read -r continue_choice
            if [[ "$continue_choice" =~ ^[Nn]$ ]]; then
                break
            fi
        done
    else
        # Command line mode
        case "$1" in
            "crypto")
                setup_crypto_exchange
                ;;
            "forex")
                setup_forex_broker
                ;;
            "env")
                setup_environment
                ;;
            "validate")
                validate_setup
                ;;
            *)
                echo "Usage: $0 [crypto|forex|env|validate]"
                echo "Or run without arguments for interactive mode"
                exit 1
                ;;
        esac
    fi
    
    echo
    print_success "Setup completed!"
    print_info "Next steps:"
    print_info "1. Review your account configurations"
    print_info "2. Test with sandbox/demo accounts first"
    print_info "3. Run: ./scripts/trading_bot.sh validate"
    print_info "4. Start trading: ./scripts/trading_bot.sh start"
}

# Run main function
main "$@"