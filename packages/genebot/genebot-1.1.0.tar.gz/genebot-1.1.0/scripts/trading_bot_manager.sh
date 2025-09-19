#!/bin/bash
# Trading Bot Manager - Master Control Script
# This script provides a unified interface to all trading bot operations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Available scripts
TRADING_BOT_SCRIPT="$SCRIPT_DIR/trading_bot.sh"
SETUP_SCRIPT="$SCRIPT_DIR/setup_accounts.sh"
REPORTS_SCRIPT="$SCRIPT_DIR/generate_reports.sh"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor_bot.sh"

print_header() {
    echo -e "${CYAN}${1}${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..70})${NC}"
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

print_menu_item() {
    echo -e "${MAGENTA}$1${NC} $2"
}

# Function to check script availability
check_scripts() {
    local missing_scripts=()
    
    if [[ ! -f "$TRADING_BOT_SCRIPT" ]]; then
        missing_scripts+=("trading_bot.sh")
    fi
    
    if [[ ! -f "$SETUP_SCRIPT" ]]; then
        missing_scripts+=("setup_accounts.sh")
    fi
    
    if [[ ! -f "$REPORTS_SCRIPT" ]]; then
        missing_scripts+=("generate_reports.sh")
    fi
    
    if [[ ! -f "$MONITOR_SCRIPT" ]]; then
        missing_scripts+=("monitor_bot.sh")
    fi
    
    if [[ ${#missing_scripts[@]} -gt 0 ]]; then
        print_error "Missing required scripts: ${missing_scripts[*]}"
        return 1
    fi
    
    return 0
}

# Function to show main menu
show_main_menu() {
    clear
    print_header "🤖 Trading Bot Manager - Master Control Panel"
    
    echo -e "${CYAN}Welcome to the Trading Bot Management System${NC}"
    echo -e "${BLUE}Select an operation category:${NC}"
    echo
    
    print_menu_item "1." "Account Management - Setup and manage exchange/broker accounts"
    print_menu_item "2." "Bot Control - Start, stop, and control the trading bot"
    print_menu_item "3." "Monitoring - Real-time monitoring and health checks"
    print_menu_item "4." "Reports - Generate trading reports and analytics"
    print_menu_item "5." "Quick Actions - Common operations and shortcuts"
    print_menu_item "6." "System Info - System status and diagnostics"
    print_menu_item "7." "Help & Documentation - Get help and view guides"
    print_menu_item "8." "Exit - Close the manager"
    echo
}

# Function to show account management menu
show_account_menu() {
    clear
    print_header "🏦 Account Management"
    
    echo -e "${BLUE}Account Management Options:${NC}"
    echo
    
    print_menu_item "1." "Setup New Account (Interactive) - Add crypto/forex accounts"
    print_menu_item "2." "List All Accounts - View configured accounts"
    print_menu_item "3." "Validate Accounts - Check account configurations"
    print_menu_item "4." "Enable/Disable Account - Toggle account status"
    print_menu_item "5." "Remove Account - Delete account configuration"
    print_menu_item "6." "Setup Demo Accounts - Quick demo setup for testing"
    print_menu_item "7." "Backup Configuration - Backup account settings"
    print_menu_item "8." "Back to Main Menu"
    echo
}

# Function to show bot control menu
show_bot_menu() {
    clear
    print_header "🤖 Bot Control"
    
    echo -e "${BLUE}Bot Control Options:${NC}"
    echo
    
    print_menu_item "1." "Start Trading Bot - Begin automated trading"
    print_menu_item "2." "Stop Trading Bot - Stop all trading operations"
    print_menu_item "3." "Restart Trading Bot - Stop and start the bot"
    print_menu_item "4." "Bot Status - Check current bot status"
    print_menu_item "5." "Quick Health Check - Verify bot health"
    print_menu_item "6." "View Recent Activity - Show recent bot activity"
    print_menu_item "7." "Emergency Stop - Force stop all operations"
    print_menu_item "8." "Back to Main Menu"
    echo
}

# Function to show monitoring menu
show_monitoring_menu() {
    clear
    print_header "📊 Monitoring & Health"
    
    echo -e "${BLUE}Monitoring Options:${NC}"
    echo
    
    print_menu_item "1." "Real-time Dashboard - Live status dashboard"
    print_menu_item "2." "Continuous Monitoring - Auto-refresh monitoring"
    print_menu_item "3." "Alert Monitoring - Background monitoring with alerts"
    print_menu_item "4." "Performance Metrics - View performance statistics"
    print_menu_item "5." "View Logs - Show recent log entries"
    print_menu_item "6." "Follow Logs - Real-time log streaming"
    print_menu_item "7." "System Health Check - Comprehensive health check"
    print_menu_item "8." "Back to Main Menu"
    echo
}

# Function to show reports menu
show_reports_menu() {
    clear
    print_header "📈 Reports & Analytics"
    
    echo -e "${BLUE}Report Generation Options:${NC}"
    echo
    
    print_menu_item "1." "Quick Reports - Fast console reports"
    print_menu_item "2." "Daily Reports - Generate today's reports"
    print_menu_item "3." "Weekly Reports - Generate weekly reports"
    print_menu_item "4." "Monthly Reports - Generate monthly reports"
    print_menu_item "5." "Custom Reports - Custom date range reports"
    print_menu_item "6." "List Existing Reports - View saved reports"
    print_menu_item "7." "Setup Automated Reports - Schedule automatic reports"
    print_menu_item "8." "Back to Main Menu"
    echo
}

# Function to show quick actions menu
show_quick_menu() {
    clear
    print_header "⚡ Quick Actions"
    
    echo -e "${BLUE}Quick Action Options:${NC}"
    echo
    
    print_menu_item "1." "Full System Status - Complete status overview"
    print_menu_item "2." "Today's Summary - Quick performance summary"
    print_menu_item "3." "Setup Demo Environment - Complete demo setup"
    print_menu_item "4." "Validate Everything - Full system validation"
    print_menu_item "5." "Emergency Procedures - Emergency operations"
    print_menu_item "6." "System Cleanup - Clean logs and old files"
    print_menu_item "7." "Backup Everything - Complete system backup"
    print_menu_item "8." "Back to Main Menu"
    echo
}

# Function to show system info
show_system_info() {
    clear
    print_header "💻 System Information"
    
    echo -e "${BLUE}System Details:${NC}"
    echo
    
    # Operating System
    echo -e "${CYAN}Operating System:${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS $(sw_vers -productVersion)"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  $(lsb_release -d | cut -f2)"
    else
        echo "  $OSTYPE"
    fi
    
    # Python Version
    echo -e "${CYAN}Python Version:${NC}"
    python --version | sed 's/^/  /'
    
    # Project Location
    echo -e "${CYAN}Project Location:${NC}"
    echo "  $PROJECT_ROOT"
    
    # Available Scripts
    echo -e "${CYAN}Available Scripts:${NC}"
    for script in "$SCRIPT_DIR"/*.sh; do
        if [[ -x "$script" ]]; then
            echo "  ✅ $(basename "$script")"
        else
            echo "  ❌ $(basename "$script") (not executable)"
        fi
    done
    
    # Configuration Status
    echo -e "${CYAN}Configuration Status:${NC}"
    if [[ -f "$PROJECT_ROOT/config/accounts.yaml" ]]; then
        echo "  ✅ Accounts configuration exists"
    else
        echo "  ❌ No accounts configured"
    fi
    
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        echo "  ✅ Environment file exists"
    else
        echo "  ⚠️  No environment file (.env)"
    fi
    
    # Log Status
    echo -e "${CYAN}Log Status:${NC}"
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    if [[ -f "$log_file" ]]; then
        local log_size=$(du -h "$log_file" | cut -f1)
        echo "  ✅ Log file exists ($log_size)"
    else
        echo "  ❌ No log file found"
    fi
    
    echo
    echo -e "${YELLOW}Press any key to continue...${NC}"
    read -n 1 -s
}

# Function to handle account management
handle_account_management() {
    while true; do
        show_account_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                "$SETUP_SCRIPT"
                ;;
            2)
                "$TRADING_BOT_SCRIPT" list
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            3)
                "$TRADING_BOT_SCRIPT" validate
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            4)
                echo
                read -p "Account name: " account_name
                read -p "Account type (crypto/forex): " account_type
                echo "1. Enable"
                echo "2. Disable"
                read -p "Select action (1-2): " action
                
                if [[ "$action" == "1" ]]; then
                    "$TRADING_BOT_SCRIPT" enable "$account_name" "$account_type"
                elif [[ "$action" == "2" ]]; then
                    "$TRADING_BOT_SCRIPT" disable "$account_name" "$account_type"
                fi
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            5)
                echo
                read -p "Account name: " account_name
                read -p "Account type (crypto/forex): " account_type
                "$TRADING_BOT_SCRIPT" remove "$account_name" "$account_type"
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            6)
                "$TRADING_BOT_SCRIPT" setup-demo
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            7)
                "$TRADING_BOT_SCRIPT" backup-config
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            8)
                break
                ;;
            *)
                print_error "Invalid choice"
                sleep 1
                ;;
        esac
    done
}

# Function to handle bot control
handle_bot_control() {
    while true; do
        show_bot_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                "$TRADING_BOT_SCRIPT" start
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            2)
                "$TRADING_BOT_SCRIPT" stop
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            3)
                "$TRADING_BOT_SCRIPT" restart
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            4)
                "$TRADING_BOT_SCRIPT" status
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            5)
                "$TRADING_BOT_SCRIPT" health-check
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            6)
                "$MONITOR_SCRIPT" logs 20
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            7)
                print_warning "Emergency stop will force terminate all bot operations"
                echo -n "Are you sure? [y/N]: "
                read -r confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    "$TRADING_BOT_SCRIPT" stop
                    print_success "Emergency stop completed"
                fi
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            8)
                break
                ;;
            *)
                print_error "Invalid choice"
                sleep 1
                ;;
        esac
    done
}

# Function to handle monitoring
handle_monitoring() {
    while true; do
        show_monitoring_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                "$MONITOR_SCRIPT" dashboard
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            2)
                echo
                read -p "Refresh interval in seconds [5]: " interval
                interval=${interval:-5}
                "$MONITOR_SCRIPT" monitor "$interval"
                ;;
            3)
                echo
                read -p "Check interval in seconds [30]: " interval
                interval=${interval:-30}
                "$MONITOR_SCRIPT" alerts "$interval"
                ;;
            4)
                "$MONITOR_SCRIPT" performance
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            5)
                echo
                read -p "Number of log lines to show [50]: " lines
                lines=${lines:-50}
                "$MONITOR_SCRIPT" logs "$lines"
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            6)
                "$MONITOR_SCRIPT" follow
                ;;
            7)
                "$MONITOR_SCRIPT" health
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            8)
                break
                ;;
            *)
                print_error "Invalid choice"
                sleep 1
                ;;
        esac
    done
}

# Function to handle reports
handle_reports() {
    while true; do
        show_reports_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                "$REPORTS_SCRIPT" quick
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            2)
                "$REPORTS_SCRIPT" daily
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            3)
                "$REPORTS_SCRIPT" weekly
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            4)
                echo
                read -p "Month (YYYY-MM) [current month]: " month
                "$REPORTS_SCRIPT" monthly "$month"
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            5)
                "$REPORTS_SCRIPT" custom
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            6)
                "$REPORTS_SCRIPT" list
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            7)
                "$REPORTS_SCRIPT" setup-cron
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            8)
                break
                ;;
            *)
                print_error "Invalid choice"
                sleep 1
                ;;
        esac
    done
}

# Function to handle quick actions
handle_quick_actions() {
    while true; do
        show_quick_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                print_header "Full System Status"
                "$TRADING_BOT_SCRIPT" status
                echo
                "$TRADING_BOT_SCRIPT" list
                echo
                "$MONITOR_SCRIPT" health
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            2)
                "$REPORTS_SCRIPT" quick
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            3)
                print_header "Setting up Demo Environment"
                "$TRADING_BOT_SCRIPT" setup-demo
                "$TRADING_BOT_SCRIPT" validate
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            4)
                print_header "Full System Validation"
                "$TRADING_BOT_SCRIPT" validate
                "$TRADING_BOT_SCRIPT" health-check
                "$MONITOR_SCRIPT" health
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            5)
                print_header "Emergency Procedures"
                echo "1. Emergency Stop Bot"
                echo "2. Cleanup Demo Accounts"
                echo "3. Reset Configuration"
                read -p "Select emergency action (1-3): " emergency_choice
                
                case "$emergency_choice" in
                    1)
                        "$TRADING_BOT_SCRIPT" stop
                        ;;
                    2)
                        "$TRADING_BOT_SCRIPT" cleanup-demo
                        ;;
                    3)
                        print_warning "This will remove all account configurations"
                        echo -n "Are you sure? [y/N]: "
                        read -r confirm
                        if [[ "$confirm" =~ ^[Yy]$ ]]; then
                            rm -f "$PROJECT_ROOT/config/accounts.yaml"
                            print_success "Configuration reset"
                        fi
                        ;;
                esac
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            6)
                print_header "System Cleanup"
                "$REPORTS_SCRIPT" clean
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            7)
                "$TRADING_BOT_SCRIPT" backup-config
                echo -e "\n${YELLOW}Press any key to continue...${NC}"
                read -n 1 -s
                ;;
            8)
                break
                ;;
            *)
                print_error "Invalid choice"
                sleep 1
                ;;
        esac
    done
}

# Function to show help
show_help() {
    clear
    print_header "📚 Help & Documentation"
    
    echo -e "${BLUE}Available Documentation:${NC}"
    echo
    
    local docs_dir="$PROJECT_ROOT/docs"
    if [[ -d "$docs_dir" ]]; then
        echo -e "${CYAN}Documentation Files:${NC}"
        for doc in "$docs_dir"/*.md; do
            if [[ -f "$doc" ]]; then
                echo "  📄 $(basename "$doc")"
            fi
        done
        echo
    fi
    
    echo -e "${CYAN}Quick Help:${NC}"
    echo "  🏦 Account Management: Setup and manage trading accounts"
    echo "  🤖 Bot Control: Start, stop, and monitor the trading bot"
    echo "  📊 Monitoring: Real-time status and health monitoring"
    echo "  📈 Reports: Generate trading reports and analytics"
    echo "  ⚡ Quick Actions: Common operations and shortcuts"
    echo
    
    echo -e "${CYAN}Command Line Usage:${NC}"
    echo "  ./scripts/trading_bot.sh <command>        # Bot operations"
    echo "  ./scripts/setup_accounts.sh               # Account setup"
    echo "  ./scripts/generate_reports.sh <type>      # Report generation"
    echo "  ./scripts/monitor_bot.sh <command>        # Monitoring"
    echo
    
    echo -e "${CYAN}Getting Started:${NC}"
    echo "  1. Setup accounts: Account Management → Setup New Account"
    echo "  2. Validate setup: Account Management → Validate Accounts"
    echo "  3. Start bot: Bot Control → Start Trading Bot"
    echo "  4. Monitor: Monitoring → Real-time Dashboard"
    echo
    
    echo -e "${YELLOW}Press any key to continue...${NC}"
    read -n 1 -s
}

# Main execution loop
main() {
    # Check if required scripts exist
    if ! check_scripts; then
        print_error "Required scripts are missing. Please ensure all scripts are present."
        exit 1
    fi
    
    # Main menu loop
    while true; do
        show_main_menu
        read -p "Select option (1-8): " choice
        
        case "$choice" in
            1)
                handle_account_management
                ;;
            2)
                handle_bot_control
                ;;
            3)
                handle_monitoring
                ;;
            4)
                handle_reports
                ;;
            5)
                handle_quick_actions
                ;;
            6)
                show_system_info
                ;;
            7)
                show_help
                ;;
            8)
                clear
                print_success "Thank you for using Trading Bot Manager!"
                print_info "Happy trading! 🚀"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please select 1-8."
                sleep 1
                ;;
        esac
    done
}

# Run main function
main "$@"