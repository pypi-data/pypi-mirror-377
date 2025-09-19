#!/bin/bash
# Trading Bot CLI Wrapper Script
# This script provides convenient shortcuts for common trading bot CLI operations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLI_SCRIPT="$SCRIPT_DIR/trading_bot_cli.py"

# Check if CLI script exists
if [[ ! -f "$CLI_SCRIPT" ]]; then
    echo -e "${RED}❌ CLI script not found: $CLI_SCRIPT${NC}"
    exit 1
fi

# Function to print colored output
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

# Function to run CLI command with error handling
run_cli() {
    local cmd="$1"
    shift
    
    print_info "Running: $cmd $*"
    if python "$CLI_SCRIPT" "$cmd" "$@"; then
        print_success "Command completed successfully"
        return 0
    else
        print_error "Command failed"
        return 1
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Trading Bot CLI Wrapper Script

Usage: $0 <command> [options]

ACCOUNT MANAGEMENT:
  add-crypto              Add a crypto exchange account (interactive)
  add-forex               Add a forex broker account (interactive)
  edit-crypto <name>      Edit a crypto exchange account (interactive)
  edit-forex <name>       Edit a forex broker account (interactive)
  list                    List all configured accounts
  list-exchanges          List all available CCXT crypto exchanges
  list-brokers            List all available forex brokers
  validate                Validate all account configurations
  enable <name> <type>    Enable an account (crypto/forex)
  disable <name> <type>   Disable an account (crypto/forex)
  remove <name> <type>    Remove an account (crypto/forex)
  remove-all              Remove all accounts (with confirmation)
  remove-by-exchange <ex> Remove all accounts for specific exchange
  remove-by-type <type>   Remove all accounts of type (crypto/forex)

BOT CONTROL:
  start                   Start the trading bot
  stop                    Stop the trading bot
  status                  Show bot status
  restart                 Restart the trading bot
  reset                   Reset system (clean up all data)

REPORTING:
  report-summary          Generate summary report (last 30 days)
  report-detailed         Generate detailed report (last 30 days)
  report-performance      Generate performance report (last 30 days)
  report-compliance       Generate compliance report (last 30 days)
  report-custom           Generate custom report with date range

UTILITIES:
  setup-demo              Setup demo accounts for testing
  cleanup-demo            Remove demo accounts
  backup-config           Backup account configurations
  restore-config          Restore account configurations
  health-check            Perform system health check
  reset [--force] [--accounts] [--docker] [--venv]  Reset system and clean up all data

EXAMPLES:
  $0 add-crypto                           # Add crypto exchange interactively
  $0 edit-crypto binance                  # Edit binance exchange account
  $0 list                                 # List all accounts
  $0 validate                             # Validate accounts
  $0 start                                # Start trading bot
  $0 report-summary                       # Generate summary report
  $0 enable binance crypto                # Enable binance account
  $0 setup-demo                           # Setup demo accounts
  $0 remove-all                           # Remove all accounts (with confirmation)
  $0 remove-by-exchange binance           # Remove all binance accounts
  $0 remove-by-type crypto                # Remove all crypto accounts
  $0 reset                                # Clean up all data (with confirmation)
  $0 reset --force --accounts             # Force reset including accounts

For detailed help on specific commands:
  $0 help <command>

EOF
}

# Function to show detailed help for specific commands
show_command_help() {
    local command="$1"
    
    case "$command" in
        "add-crypto")
            python "$CLI_SCRIPT" add-crypto --help
            ;;
        "add-forex")
            python "$CLI_SCRIPT" add-forex --help
            ;;
        "list-exchanges")
            python "$CLI_SCRIPT" list-exchanges --help
            ;;
        "list-brokers")
            python "$CLI_SCRIPT" list-brokers --help
            ;;
        "report")
            python "$CLI_SCRIPT" report --help
            ;;
        "reset")
            cat << EOF
Reset Command - Clean Up All System Data

USAGE:
  $0 reset [OPTIONS]

OPTIONS:
  --force      Skip confirmation prompt
  --accounts   Also reset account configurations
  --docker     Also clean up Docker containers and images
  --venv       Also reset Python virtual environment

WHAT GETS CLEANED:
  • All log files and directories (logs/)
  • All report files (reports/, backtest_reports/)
  • All database files (*.db, *.sqlite)
  • All cache directories (__pycache__, .pytest_cache)
  • All temporary files (*.tmp, *.bak, debug_*.py)
  • All backup files and directories
  • All PID files

WHAT GETS PRESERVED:
  • Source code (src/, scripts/, examples/)
  • Documentation (docs/, *.md files)
  • Configuration templates (*.example.yaml)
  • Requirements files (requirements*.txt)
  • Account configurations (unless --accounts used)
  • Virtual environment (unless --venv used)

EXAMPLES:
  $0 reset                    # Interactive reset (with confirmation)
  $0 reset --force            # Skip confirmation
  $0 reset --accounts         # Also reset account configurations
  $0 reset --force --venv     # Force reset including virtual environment
  $0 reset --docker           # Also clean up Docker resources

WARNING: This operation is irreversible!
EOF
            ;;
        *)
            echo -e "${YELLOW}No detailed help available for: $command${NC}"
            echo "Try: python $CLI_SCRIPT $command --help"
            ;;
    esac
}

# Function to setup demo accounts
setup_demo_accounts() {
    print_header "Setting Up Demo Accounts"
    
    print_info "Adding Binance demo account..."
    run_cli add-crypto \
        --name "binance-demo" \
        --exchange-type "binance" \
        --api-key "demo_binance_api_key_12345" \
        --api-secret "demo_binance_api_secret_67890" \
        --sandbox \
        --enabled \
        --force
    
    print_info "Adding Coinbase demo account..."
    run_cli add-crypto \
        --name "coinbase-demo" \
        --exchange-type "coinbase" \
        --api-key "demo_coinbase_api_key" \
        --api-secret "demo_coinbase_api_secret" \
        --api-passphrase "demo_coinbase_passphrase" \
        --sandbox \
        --enabled \
        --force
    
    print_info "Adding OANDA demo account..."
    run_cli add-forex \
        --name "oanda-demo" \
        --broker-type "oanda" \
        --api-key "demo_oanda_api_key" \
        --account-id "101-001-12345678-001" \
        --sandbox \
        --enabled \
        --force
    
    print_info "Adding MT5 demo account..."
    run_cli add-forex \
        --name "mt5-demo" \
        --broker-type "mt5" \
        --server "Demo-Server" \
        --login "12345678" \
        --password "demo_password" \
        --sandbox \
        --enabled \
        --force
    
    print_success "Demo accounts setup completed!"
    echo
    run_cli list-accounts
}

# Function to cleanup demo accounts
cleanup_demo_accounts() {
    print_header "Cleaning Up Demo Accounts"
    
    # List of demo accounts to remove
    demo_accounts=(
        "binance-demo crypto"
        "coinbase-demo crypto"
        "oanda-demo forex"
        "mt5-demo forex"
    )
    
    for account in "${demo_accounts[@]}"; do
        read -ra parts <<< "$account"
        name="${parts[0]}"
        type="${parts[1]}"
        
        print_info "Removing $name ($type)..."
        if run_cli remove-account "$name" "$type" 2>/dev/null; then
            print_success "Removed $name"
        else
            print_warning "$name not found or already removed"
        fi
    done
    
    print_success "Demo cleanup completed!"
    echo
    run_cli list-accounts
}

# Function to backup configurations
backup_config() {
    print_header "Backing Up Configurations"
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$PROJECT_ROOT/$backup_dir"
    
    # Files to backup
    local files_to_backup=(
        "config/accounts.yaml"
        "config/trading_bot_config.yaml"
        ".env"
    )
    
    for file in "${files_to_backup[@]}"; do
        local full_path="$PROJECT_ROOT/$file"
        if [[ -f "$full_path" ]]; then
            cp "$full_path" "$PROJECT_ROOT/$backup_dir/"
            print_success "Backed up: $file"
        else
            print_warning "File not found: $file"
        fi
    done
    
    print_success "Configuration backed up to: $backup_dir"
}

# Function to perform health check
health_check() {
    print_header "System Health Check"
    
    # Check Python
    if command -v python &> /dev/null; then
        python_version=$(python --version 2>&1)
        print_success "Python: $python_version"
    else
        print_error "Python not found"
        return 1
    fi
    
    # Check required packages
    local required_packages=("colorama" "tabulate" "yaml" "pydantic")
    for package in "${required_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            print_success "Package: $package"
        else
            print_error "Missing package: $package"
        fi
    done
    
    # Check CLI script
    if [[ -f "$CLI_SCRIPT" ]]; then
        print_success "CLI script found"
    else
        print_error "CLI script not found"
        return 1
    fi
    
    # Check configuration directories
    local config_dirs=("config" "logs" "reports")
    for dir in "${config_dirs[@]}"; do
        local full_dir="$PROJECT_ROOT/$dir"
        if [[ -d "$full_dir" ]]; then
            print_success "Directory: $dir"
        else
            print_warning "Directory missing: $dir (will be created as needed)"
        fi
    done
    
    # Test CLI functionality
    print_info "Testing CLI functionality..."
    if python "$CLI_SCRIPT" --help &>/dev/null; then
        print_success "CLI functionality test passed"
    else
        print_error "CLI functionality test failed"
        return 1
    fi
    
    print_success "Health check completed!"
}

# Function to generate custom report
generate_custom_report() {
    print_header "Generate Custom Report"
    
    echo "Report Types:"
    echo "1. Summary"
    echo "2. Detailed"
    echo "3. Performance"
    echo "4. Compliance"
    echo
    
    read -p "Select report type (1-4): " report_choice
    
    case "$report_choice" in
        1) report_type="summary" ;;
        2) report_type="detailed" ;;
        3) report_type="performance" ;;
        4) report_type="compliance" ;;
        *) 
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    read -p "Start date (YYYY-MM-DD) [default: 30 days ago]: " start_date
    read -p "End date (YYYY-MM-DD) [default: today]: " end_date
    read -p "Output file (optional): " output_file
    
    local cmd_args=("--type" "$report_type")
    
    if [[ -n "$start_date" ]]; then
        cmd_args+=("--start-date" "$start_date")
    fi
    
    if [[ -n "$end_date" ]]; then
        cmd_args+=("--end-date" "$end_date")
    fi
    
    if [[ -n "$output_file" ]]; then
        cmd_args+=("--output" "$output_file")
    fi
    
    run_cli report "${cmd_args[@]}"
}

# Main command processing
case "${1:-}" in
    # Account management
    "add-crypto")
        run_cli add-crypto
        ;;
    "add-forex")
        run_cli add-forex
        ;;
    "edit-crypto")
        if [[ $# -ne 2 ]]; then
            print_error "Usage: $0 edit-crypto <account-name>"
            exit 1
        fi
        run_cli edit-crypto "$2"
        ;;
    "edit-forex")
        if [[ $# -ne 2 ]]; then
            print_error "Usage: $0 edit-forex <account-name>"
            exit 1
        fi
        run_cli edit-forex "$2"
        ;;
    "list")
        run_cli list-accounts
        ;;
    "list-exchanges")
        run_cli list-exchanges
        ;;
    "list-brokers")
        run_cli list-brokers
        ;;
    "validate")
        run_cli validate-accounts
        ;;
    "enable")
        if [[ $# -ne 3 ]]; then
            print_error "Usage: $0 enable <name> <type>"
            exit 1
        fi
        run_cli enable-account "$2" "$3"
        ;;
    "disable")
        if [[ $# -ne 3 ]]; then
            print_error "Usage: $0 disable <name> <type>"
            exit 1
        fi
        run_cli disable-account "$2" "$3"
        ;;
    "remove")
        if [[ $# -ne 3 ]]; then
            print_error "Usage: $0 remove <name> <type>"
            exit 1
        fi
        echo -e "${YELLOW}Are you sure you want to remove account '$2' ($3)? [y/N]${NC}"
        read -r confirmation
        if [[ "$confirmation" =~ ^[Yy]$ ]]; then
            run_cli remove-account "$2" "$3"
        else
            print_info "Operation cancelled"
        fi
        ;;
    "remove-all")
        # Pass --force flag if provided
        if [[ "$2" == "--force" ]]; then
            run_cli remove-all-accounts --force
        else
            run_cli remove-all-accounts
        fi
        ;;
    "remove-by-exchange")
        if [[ $# -lt 2 ]]; then
            print_error "Usage: $0 remove-by-exchange <exchange> [--force]"
            exit 1
        fi
        if [[ "$3" == "--force" ]]; then
            run_cli remove-by-exchange "$2" --force
        else
            run_cli remove-by-exchange "$2"
        fi
        ;;
    "remove-by-type")
        if [[ $# -lt 2 ]]; then
            print_error "Usage: $0 remove-by-type <crypto|forex> [--force]"
            exit 1
        fi
        if [[ "$3" == "--force" ]]; then
            run_cli remove-by-type "$2" --force
        else
            run_cli remove-by-type "$2"
        fi
        ;;
    
    # Bot control
    "start")
        run_cli start
        ;;
    "stop")
        run_cli stop
        ;;
    "status")
        run_cli status
        ;;
    "restart")
        print_info "Stopping bot..."
        run_cli stop
        sleep 2
        print_info "Starting bot..."
        run_cli start
        ;;
    
    # Reporting
    "report-summary")
        run_cli report --type summary
        ;;
    "report-detailed")
        run_cli report --type detailed
        ;;
    "report-performance")
        run_cli report --type performance
        ;;
    "report-compliance")
        run_cli report --type compliance
        ;;
    "report-custom")
        generate_custom_report
        ;;
    
    # Utilities
    "setup-demo")
        setup_demo_accounts
        ;;
    "cleanup-demo")
        cleanup_demo_accounts
        ;;
    "backup-config")
        backup_config
        ;;
    "health-check")
        health_check
        ;;
    "reset")
        # Pass all arguments to the reset command
        shift  # Remove 'reset' from arguments
        run_cli reset "$@"
        ;;
    
    # Help
    "help")
        if [[ -n "${2:-}" ]]; then
            show_command_help "$2"
        else
            show_usage
        fi
        ;;
    
    # Default
    "")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_usage
        exit 1
        ;;
esac