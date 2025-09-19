#!/bin/bash
# Trading Bot Monitoring Script
# This script monitors the trading bot status and provides real-time information

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
CLI_SCRIPT="$SCRIPT_DIR/trading_bot_cli.py"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

print_status() {
    echo -e "${MAGENTA}📊 ${1}${NC}"
}

# Function to get current timestamp
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Function to check bot status
check_bot_status() {
    if python "$CLI_SCRIPT" status >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get account status
get_account_status() {
    local temp_file=$(mktemp)
    if python "$CLI_SCRIPT" list-accounts > "$temp_file" 2>/dev/null; then
        local total_accounts=$(grep -o "Summary: [0-9]* total accounts" "$temp_file" | grep -o "[0-9]*" | head -1)
        local enabled_accounts=$(grep -o "[0-9]* enabled" "$temp_file" | grep -o "[0-9]*")
        echo "${enabled_accounts:-0}/${total_accounts:-0}"
    else
        echo "N/A"
    fi
    rm -f "$temp_file"
}

# Function to check system resources
check_system_resources() {
    local cpu_usage=""
    local memory_usage=""
    local disk_usage=""
    
    # CPU usage (macOS/Linux compatible)
    if command -v top >/dev/null 2>&1; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            cpu_usage=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
        else
            # Linux
            cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        fi
    fi
    
    # Memory usage
    if command -v free >/dev/null 2>&1; then
        # Linux
        memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        memory_usage=$(vm_stat | awk '
            /Pages free/ { free = $3 }
            /Pages active/ { active = $3 }
            /Pages inactive/ { inactive = $3 }
            /Pages speculative/ { speculative = $3 }
            /Pages wired down/ { wired = $4 }
            END { 
                total = (free + active + inactive + speculative + wired) * 4096 / 1024 / 1024
                used = (active + inactive + wired) * 4096 / 1024 / 1024
                printf "%.1f", used/total * 100
            }')
    fi
    
    # Disk usage
    disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    echo "CPU: ${cpu_usage:-N/A}% | Memory: ${memory_usage:-N/A}% | Disk: ${disk_usage:-N/A}%"
}

# Function to check log files
check_log_status() {
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    
    if [[ -f "$log_file" ]]; then
        local log_size=$(du -h "$log_file" | cut -f1)
        local last_modified=$(date -r "$log_file" '+%H:%M:%S')
        local error_count=$(grep -c "ERROR" "$log_file" 2>/dev/null || echo "0")
        local warning_count=$(grep -c "WARNING" "$log_file" 2>/dev/null || echo "0")
        
        echo "Size: $log_size | Modified: $last_modified | Errors: $error_count | Warnings: $warning_count"
    else
        echo "No log file found"
    fi
}

# Function to display dashboard
show_dashboard() {
    clear
    print_header "Trading Bot Monitoring Dashboard"
    
    local timestamp=$(get_timestamp)
    echo -e "${CYAN}Last Updated: $timestamp${NC}"
    echo
    
    # Bot Status
    print_status "Bot Status:"
    if check_bot_status; then
        python "$CLI_SCRIPT" status 2>/dev/null | grep -E "(Bot Status|Last Started|Uptime)" || echo "Status information unavailable"
    else
        print_error "Bot is not responding"
    fi
    echo
    
    # Account Status
    print_status "Account Status:"
    local account_status=$(get_account_status)
    echo "Active Accounts: $account_status"
    echo
    
    # System Resources
    print_status "System Resources:"
    check_system_resources
    echo
    
    # Log Status
    print_status "Log Status:"
    check_log_status
    echo
    
    # Recent Activity (if log file exists)
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    if [[ -f "$log_file" ]]; then
        print_status "Recent Activity (last 5 lines):"
        tail -5 "$log_file" 2>/dev/null | while read -r line; do
            echo "  $line"
        done
    fi
    
    echo
    echo -e "${YELLOW}Press Ctrl+C to exit monitoring${NC}"
}

# Function to monitor continuously
monitor_continuous() {
    local refresh_interval="${1:-5}"
    
    print_info "Starting continuous monitoring (refresh every ${refresh_interval}s)"
    print_info "Press Ctrl+C to stop"
    
    trap 'echo -e "\n${YELLOW}Monitoring stopped${NC}"; exit 0' INT
    
    while true; do
        show_dashboard
        sleep "$refresh_interval"
    done
}

# Function to monitor with alerts
monitor_with_alerts() {
    local check_interval="${1:-30}"
    local alert_file="$PROJECT_ROOT/logs/monitor_alerts.log"
    
    mkdir -p "$(dirname "$alert_file")"
    
    print_info "Starting alert monitoring (check every ${check_interval}s)"
    print_info "Alerts will be logged to: $alert_file"
    print_info "Press Ctrl+C to stop"
    
    trap 'echo -e "\n${YELLOW}Alert monitoring stopped${NC}"; exit 0' INT
    
    local last_bot_status="unknown"
    local alert_count=0
    
    while true; do
        local timestamp=$(get_timestamp)
        local current_bot_status="down"
        
        # Check bot status
        if check_bot_status; then
            current_bot_status="up"
        fi
        
        # Alert on status change
        if [[ "$current_bot_status" != "$last_bot_status" && "$last_bot_status" != "unknown" ]]; then
            local alert_msg="[$timestamp] Bot status changed: $last_bot_status -> $current_bot_status"
            echo "$alert_msg" >> "$alert_file"
            
            if [[ "$current_bot_status" == "down" ]]; then
                print_error "ALERT: Bot went down at $timestamp"
                ((alert_count++))
            else
                print_success "ALERT: Bot came back up at $timestamp"
            fi
        fi
        
        # Check for errors in logs
        local log_file="$PROJECT_ROOT/logs/trading_bot.log"
        if [[ -f "$log_file" ]]; then
            local recent_errors=$(tail -100 "$log_file" | grep -c "ERROR" || echo "0")
            if [[ "$recent_errors" -gt 0 ]]; then
                local error_msg="[$timestamp] Found $recent_errors recent errors in log"
                echo "$error_msg" >> "$alert_file"
                print_warning "Found $recent_errors recent errors in log"
            fi
        fi
        
        # Status update
        echo -e "${BLUE}[$timestamp] Status: $current_bot_status | Alerts: $alert_count${NC}"
        
        last_bot_status="$current_bot_status"
        sleep "$check_interval"
    done
}

# Function to show performance metrics
show_performance() {
    print_header "Performance Metrics"
    
    # Generate quick performance report
    print_info "Generating performance summary..."
    python "$CLI_SCRIPT" report --type performance 2>/dev/null || print_warning "Could not generate performance report"
    
    echo
    print_status "System Performance:"
    check_system_resources
    
    echo
    print_status "Account Status:"
    python "$CLI_SCRIPT" list-accounts 2>/dev/null | grep -E "(Crypto Exchanges|Forex Brokers|Summary)" || print_warning "Could not get account status"
}

# Function to show recent logs
show_logs() {
    local lines="${1:-50}"
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    
    print_header "Recent Log Entries (last $lines lines)"
    
    if [[ -f "$log_file" ]]; then
        tail -"$lines" "$log_file" | while read -r line; do
            # Color code log levels
            if [[ "$line" == *"ERROR"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ "$line" == *"WARNING"* ]]; then
                echo -e "${YELLOW}$line${NC}"
            elif [[ "$line" == *"INFO"* ]]; then
                echo -e "${GREEN}$line${NC}"
            else
                echo "$line"
            fi
        done
    else
        print_warning "Log file not found: $log_file"
    fi
}

# Function to follow logs in real-time
follow_logs() {
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    
    print_header "Following Logs in Real-Time"
    print_info "Press Ctrl+C to stop"
    
    if [[ -f "$log_file" ]]; then
        tail -f "$log_file" | while read -r line; do
            local timestamp=$(echo "$line" | cut -d' ' -f1-2)
            local level=$(echo "$line" | grep -o -E "(DEBUG|INFO|WARNING|ERROR|CRITICAL)" | head -1)
            
            case "$level" in
                "ERROR"|"CRITICAL")
                    echo -e "${RED}$line${NC}"
                    ;;
                "WARNING")
                    echo -e "${YELLOW}$line${NC}"
                    ;;
                "INFO")
                    echo -e "${GREEN}$line${NC}"
                    ;;
                "DEBUG")
                    echo -e "${BLUE}$line${NC}"
                    ;;
                *)
                    echo "$line"
                    ;;
            esac
        done
    else
        print_error "Log file not found: $log_file"
        print_info "Start the trading bot to generate logs"
    fi
}

# Function to check health
check_health() {
    print_header "Health Check"
    
    local health_score=0
    local max_score=5
    
    # Check 1: Bot responsiveness
    print_info "Checking bot responsiveness..."
    if check_bot_status; then
        print_success "Bot is responsive"
        ((health_score++))
    else
        print_error "Bot is not responsive"
    fi
    
    # Check 2: Account configuration
    print_info "Checking account configuration..."
    if python "$CLI_SCRIPT" validate-accounts >/dev/null 2>&1; then
        print_success "Account configuration is valid"
        ((health_score++))
    else
        print_error "Account configuration has issues"
    fi
    
    # Check 3: Log file accessibility
    print_info "Checking log file..."
    local log_file="$PROJECT_ROOT/logs/trading_bot.log"
    if [[ -f "$log_file" && -r "$log_file" ]]; then
        print_success "Log file is accessible"
        ((health_score++))
    else
        print_warning "Log file not found or not readable"
    fi
    
    # Check 4: Recent activity
    print_info "Checking recent activity..."
    if [[ -f "$log_file" ]]; then
        local last_activity=$(stat -c %Y "$log_file" 2>/dev/null || stat -f %m "$log_file" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_activity))
        
        if [[ $time_diff -lt 300 ]]; then  # Less than 5 minutes
            print_success "Recent activity detected"
            ((health_score++))
        else
            print_warning "No recent activity (last activity: $((time_diff/60)) minutes ago)"
        fi
    fi
    
    # Check 5: System resources
    print_info "Checking system resources..."
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ "${disk_usage:-100}" -lt 90 ]]; then
        print_success "System resources are adequate"
        ((health_score++))
    else
        print_warning "System resources may be constrained"
    fi
    
    echo
    print_status "Health Score: $health_score/$max_score"
    
    if [[ $health_score -eq $max_score ]]; then
        print_success "System is healthy"
    elif [[ $health_score -ge 3 ]]; then
        print_warning "System has minor issues"
    else
        print_error "System has significant issues"
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Trading Bot Monitoring Script

Usage: $0 <command> [options]

COMMANDS:
  dashboard              Show real-time dashboard (one-time)
  monitor [interval]     Continuous monitoring (default: 5s refresh)
  alerts [interval]      Monitor with alerts (default: 30s check)
  performance            Show performance metrics
  logs [lines]           Show recent log entries (default: 50 lines)
  follow                 Follow logs in real-time
  health                 Perform health check
  status                 Quick status check
  help                   Show this help message

EXAMPLES:
  $0 dashboard           # Show current status dashboard
  $0 monitor 10          # Monitor with 10-second refresh
  $0 alerts 60           # Check for alerts every 60 seconds
  $0 performance         # Show performance metrics
  $0 logs 100            # Show last 100 log entries
  $0 follow              # Follow logs in real-time
  $0 health              # Perform comprehensive health check

MONITORING FEATURES:
  - Real-time bot status
  - Account configuration status
  - System resource usage
  - Log file monitoring
  - Error and warning detection
  - Alert notifications
  - Performance metrics

TIPS:
  - Use 'monitor' for continuous dashboard updates
  - Use 'alerts' for background monitoring with notifications
  - Use 'follow' to watch logs in real-time
  - Use 'health' for comprehensive system checks

EOF
}

# Main command processing
case "${1:-}" in
    "dashboard")
        show_dashboard
        ;;
    "monitor")
        monitor_continuous "${2:-5}"
        ;;
    "alerts")
        monitor_with_alerts "${2:-30}"
        ;;
    "performance")
        show_performance
        ;;
    "logs")
        show_logs "${2:-50}"
        ;;
    "follow")
        follow_logs
        ;;
    "health")
        check_health
        ;;
    "status")
        print_header "Quick Status Check"
        python "$CLI_SCRIPT" status 2>/dev/null || print_error "Bot is not responding"
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
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