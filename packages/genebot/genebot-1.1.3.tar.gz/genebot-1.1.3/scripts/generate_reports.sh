#!/bin/bash
# Trading Bot Report Generation Script
# This script generates various trading reports and manages report scheduling

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
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLI_SCRIPT="$SCRIPT_DIR/trading_bot_cli.py"
REPORTS_DIR="$PROJECT_ROOT/reports"

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

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Function to generate date-based filename
generate_filename() {
    local report_type="$1"
    local start_date="$2"
    local end_date="$3"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    if [[ -n "$start_date" && -n "$end_date" ]]; then
        echo "${report_type}_${start_date}_to_${end_date}_${timestamp}.txt"
    else
        echo "${report_type}_${timestamp}.txt"
    fi
}

# Function to run report generation
generate_report() {
    local report_type="$1"
    local start_date="$2"
    local end_date="$3"
    local output_file="$4"
    local description="$5"
    
    print_info "Generating $description..."
    
    local cmd_args=("report" "--type" "$report_type")
    
    if [[ -n "$start_date" ]]; then
        cmd_args+=("--start-date" "$start_date")
    fi
    
    if [[ -n "$end_date" ]]; then
        cmd_args+=("--end-date" "$end_date")
    fi
    
    if [[ -n "$output_file" ]]; then
        cmd_args+=("--output" "$output_file")
    fi
    
    if python "$CLI_SCRIPT" "${cmd_args[@]}"; then
        print_success "$description generated successfully"
        if [[ -n "$output_file" && -f "$output_file" ]]; then
            print_info "Report saved to: $output_file"
            print_info "File size: $(du -h "$output_file" | cut -f1)"
        fi
        return 0
    else
        print_error "Failed to generate $description"
        return 1
    fi
}

# Function to generate daily reports
generate_daily_reports() {
    print_header "Generating Daily Reports"
    
    local today=$(date +%Y-%m-%d)
    local report_date="${1:-$today}"
    local daily_dir="$REPORTS_DIR/daily/$report_date"
    
    mkdir -p "$daily_dir"
    
    print_info "Generating reports for: $report_date"
    
    # Summary report
    local summary_file="$daily_dir/summary_$report_date.txt"
    generate_report "summary" "$report_date" "$report_date" "$summary_file" "Daily Summary Report"
    
    # Performance report
    local performance_file="$daily_dir/performance_$report_date.txt"
    generate_report "performance" "$report_date" "$report_date" "$performance_file" "Daily Performance Report"
    
    # Compliance report
    local compliance_file="$daily_dir/compliance_$report_date.txt"
    generate_report "compliance" "$report_date" "$report_date" "$compliance_file" "Daily Compliance Report"
    
    print_success "Daily reports completed for $report_date"
    print_info "Reports saved in: $daily_dir"
}

# Function to generate weekly reports
generate_weekly_reports() {
    print_header "Generating Weekly Reports"
    
    local end_date=$(date +%Y-%m-%d)
    local start_date=$(date -d '7 days ago' +%Y-%m-%d)
    local week_dir="$REPORTS_DIR/weekly/$(date +%Y-W%U)"
    
    mkdir -p "$week_dir"
    
    print_info "Generating reports for week: $start_date to $end_date"
    
    # Summary report
    local summary_file="$week_dir/weekly_summary_$(date +%Y-W%U).txt"
    generate_report "summary" "$start_date" "$end_date" "$summary_file" "Weekly Summary Report"
    
    # Detailed report
    local detailed_file="$week_dir/weekly_detailed_$(date +%Y-W%U).txt"
    generate_report "detailed" "$start_date" "$end_date" "$detailed_file" "Weekly Detailed Report"
    
    # Performance report
    local performance_file="$week_dir/weekly_performance_$(date +%Y-W%U).txt"
    generate_report "performance" "$start_date" "$end_date" "$performance_file" "Weekly Performance Report"
    
    print_success "Weekly reports completed"
    print_info "Reports saved in: $week_dir"
}

# Function to generate monthly reports
generate_monthly_reports() {
    print_header "Generating Monthly Reports"
    
    local year_month="${1:-$(date +%Y-%m)}"
    local start_date="$year_month-01"
    local end_date=$(date -d "$start_date +1 month -1 day" +%Y-%m-%d)
    local month_dir="$REPORTS_DIR/monthly/$year_month"
    
    mkdir -p "$month_dir"
    
    print_info "Generating reports for month: $year_month"
    print_info "Date range: $start_date to $end_date"
    
    # All report types for monthly
    local report_types=("summary" "detailed" "performance" "compliance")
    
    for report_type in "${report_types[@]}"; do
        local output_file="$month_dir/monthly_${report_type}_${year_month}.txt"
        generate_report "$report_type" "$start_date" "$end_date" "$output_file" "Monthly ${report_type^} Report"
    done
    
    print_success "Monthly reports completed for $year_month"
    print_info "Reports saved in: $month_dir"
}

# Function to generate custom date range reports
generate_custom_reports() {
    print_header "Generate Custom Date Range Reports"
    
    echo "Enter date range for custom reports:"
    read -p "Start date (YYYY-MM-DD): " start_date
    read -p "End date (YYYY-MM-DD): " end_date
    
    # Validate dates
    if ! date -d "$start_date" >/dev/null 2>&1; then
        print_error "Invalid start date format"
        return 1
    fi
    
    if ! date -d "$end_date" >/dev/null 2>&1; then
        print_error "Invalid end date format"
        return 1
    fi
    
    if [[ "$start_date" > "$end_date" ]]; then
        print_error "Start date must be before end date"
        return 1
    fi
    
    local custom_dir="$REPORTS_DIR/custom/${start_date}_to_${end_date}"
    mkdir -p "$custom_dir"
    
    echo
    echo "Select report types to generate:"
    echo "1. Summary"
    echo "2. Detailed"
    echo "3. Performance"
    echo "4. Compliance"
    echo "5. All reports"
    echo
    read -p "Select option (1-5): " report_choice
    
    case "$report_choice" in
        1)
            local output_file="$custom_dir/summary_${start_date}_to_${end_date}.txt"
            generate_report "summary" "$start_date" "$end_date" "$output_file" "Custom Summary Report"
            ;;
        2)
            local output_file="$custom_dir/detailed_${start_date}_to_${end_date}.txt"
            generate_report "detailed" "$start_date" "$end_date" "$output_file" "Custom Detailed Report"
            ;;
        3)
            local output_file="$custom_dir/performance_${start_date}_to_${end_date}.txt"
            generate_report "performance" "$start_date" "$end_date" "$output_file" "Custom Performance Report"
            ;;
        4)
            local output_file="$custom_dir/compliance_${start_date}_to_${end_date}.txt"
            generate_report "compliance" "$start_date" "$end_date" "$output_file" "Custom Compliance Report"
            ;;
        5)
            local report_types=("summary" "detailed" "performance" "compliance")
            for report_type in "${report_types[@]}"; do
                local output_file="$custom_dir/${report_type}_${start_date}_to_${end_date}.txt"
                generate_report "$report_type" "$start_date" "$end_date" "$output_file" "Custom ${report_type^} Report"
            done
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    print_success "Custom reports completed"
    print_info "Reports saved in: $custom_dir"
}

# Function to generate quick reports (no file output)
generate_quick_reports() {
    print_header "Quick Reports (Console Output)"
    
    echo "Select quick report type:"
    echo "1. Today's Summary"
    echo "2. Last 7 Days Performance"
    echo "3. Last 30 Days Summary"
    echo "4. Current Month Compliance"
    echo
    read -p "Select option (1-4): " quick_choice
    
    case "$quick_choice" in
        1)
            local today=$(date +%Y-%m-%d)
            generate_report "summary" "$today" "$today" "" "Today's Summary"
            ;;
        2)
            local end_date=$(date +%Y-%m-%d)
            local start_date=$(date -d '7 days ago' +%Y-%m-%d)
            generate_report "performance" "$start_date" "$end_date" "" "Last 7 Days Performance"
            ;;
        3)
            local end_date=$(date +%Y-%m-%d)
            local start_date=$(date -d '30 days ago' +%Y-%m-%d)
            generate_report "summary" "$start_date" "$end_date" "" "Last 30 Days Summary"
            ;;
        4)
            local year_month=$(date +%Y-%m)
            local start_date="$year_month-01"
            local end_date=$(date +%Y-%m-%d)
            generate_report "compliance" "$start_date" "$end_date" "" "Current Month Compliance"
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
}

# Function to list existing reports
list_reports() {
    print_header "Existing Reports"
    
    if [[ ! -d "$REPORTS_DIR" ]]; then
        print_info "No reports directory found"
        return 0
    fi
    
    echo "Report directory structure:"
    echo
    
    # Use tree if available, otherwise use find
    if command -v tree >/dev/null 2>&1; then
        tree "$REPORTS_DIR" -I '__pycache__'
    else
        find "$REPORTS_DIR" -type f -name "*.txt" | sort | while read -r file; do
            local rel_path="${file#$REPORTS_DIR/}"
            local size=$(du -h "$file" | cut -f1)
            local date=$(date -r "$file" "+%Y-%m-%d %H:%M")
            printf "%-50s %8s %16s\n" "$rel_path" "$size" "$date"
        done
    fi
    
    echo
    local total_files=$(find "$REPORTS_DIR" -type f -name "*.txt" | wc -l)
    local total_size=$(du -sh "$REPORTS_DIR" 2>/dev/null | cut -f1 || echo "0")
    print_info "Total reports: $total_files files, $total_size"
}

# Function to clean old reports
clean_old_reports() {
    print_header "Clean Old Reports"
    
    echo "Select cleanup option:"
    echo "1. Remove reports older than 30 days"
    echo "2. Remove reports older than 90 days"
    echo "3. Remove reports older than 1 year"
    echo "4. Custom cleanup (specify days)"
    echo
    read -p "Select option (1-4): " cleanup_choice
    
    local days_old
    case "$cleanup_choice" in
        1) days_old=30 ;;
        2) days_old=90 ;;
        3) days_old=365 ;;
        4)
            read -p "Remove reports older than how many days? " days_old
            if ! [[ "$days_old" =~ ^[0-9]+$ ]]; then
                print_error "Invalid number of days"
                return 1
            fi
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    print_warning "This will remove all reports older than $days_old days"
    echo -n "Continue? [y/N]: "
    read -r confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled"
        return 0
    fi
    
    local files_to_remove=$(find "$REPORTS_DIR" -type f -name "*.txt" -mtime +$days_old)
    local count=$(echo "$files_to_remove" | grep -c . || echo "0")
    
    if [[ "$count" -eq 0 ]]; then
        print_info "No reports found older than $days_old days"
        return 0
    fi
    
    echo "$files_to_remove" | xargs rm -f
    
    # Remove empty directories
    find "$REPORTS_DIR" -type d -empty -delete 2>/dev/null || true
    
    print_success "Removed $count old report files"
}

# Function to setup automated reporting
setup_automated_reports() {
    print_header "Setup Automated Report Generation"
    
    local cron_file="/tmp/trading_bot_reports_cron"
    local script_path="$(realpath "$0")"
    
    cat > "$cron_file" << EOF
# Trading Bot Automated Reports
# Generated by setup_automated_reports

# Daily reports at 6 AM
0 6 * * * $script_path daily >/dev/null 2>&1

# Weekly reports on Sundays at 7 AM
0 7 * * 0 $script_path weekly >/dev/null 2>&1

# Monthly reports on the 1st at 8 AM
0 8 1 * * $script_path monthly >/dev/null 2>&1

# Cleanup old reports monthly on the 15th at 2 AM
0 2 15 * * $script_path clean-auto >/dev/null 2>&1
EOF
    
    echo "Proposed cron schedule:"
    echo
    cat "$cron_file"
    echo
    
    echo -n "Install this cron schedule? [y/N]: "
    read -r install_cron
    
    if [[ "$install_cron" =~ ^[Yy]$ ]]; then
        crontab "$cron_file"
        print_success "Automated reporting schedule installed"
        print_info "Use 'crontab -l' to view current schedule"
        print_info "Use 'crontab -e' to edit the schedule"
    else
        print_info "Cron schedule not installed"
        print_info "You can manually install it later with: crontab $cron_file"
    fi
    
    rm -f "$cron_file"
}

# Function to show usage
show_usage() {
    cat << EOF
Trading Bot Report Generation Script

Usage: $0 <command> [options]

COMMANDS:
  daily [date]           Generate daily reports (default: today)
  weekly                 Generate weekly reports (last 7 days)
  monthly [YYYY-MM]      Generate monthly reports (default: current month)
  custom                 Generate custom date range reports (interactive)
  quick                  Generate quick reports (console output only)
  list                   List existing reports
  clean                  Clean old reports (interactive)
  clean-auto             Clean reports older than 90 days (for automation)
  setup-cron             Setup automated report generation
  help                   Show this help message

EXAMPLES:
  $0 daily                    # Today's reports
  $0 daily 2024-01-15         # Reports for specific date
  $0 weekly                   # Last 7 days reports
  $0 monthly 2024-01          # January 2024 reports
  $0 custom                   # Interactive custom reports
  $0 quick                    # Quick console reports
  $0 list                     # List all existing reports
  $0 clean                    # Interactive cleanup
  $0 setup-cron               # Setup automated reports

REPORT TYPES:
  - Summary: Overview of trades, P&L, and performance
  - Detailed: Individual trade details and breakdowns
  - Performance: Advanced metrics and analysis
  - Compliance: Regulatory reporting and audit trails

AUTOMATION:
  Use 'setup-cron' to automatically generate:
  - Daily reports at 6 AM
  - Weekly reports on Sundays at 7 AM
  - Monthly reports on the 1st at 8 AM
  - Cleanup old reports monthly

EOF
}

# Main command processing
case "${1:-}" in
    "daily")
        generate_daily_reports "$2"
        ;;
    "weekly")
        generate_weekly_reports
        ;;
    "monthly")
        generate_monthly_reports "$2"
        ;;
    "custom")
        generate_custom_reports
        ;;
    "quick")
        generate_quick_reports
        ;;
    "list")
        list_reports
        ;;
    "clean")
        clean_old_reports
        ;;
    "clean-auto")
        # Automated cleanup (90 days)
        find "$REPORTS_DIR" -type f -name "*.txt" -mtime +90 -delete 2>/dev/null || true
        find "$REPORTS_DIR" -type d -empty -delete 2>/dev/null || true
        ;;
    "setup-cron")
        setup_automated_reports
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