#!/usr/bin/env python3
"""
Log Viewer Utility for CxrruptPad
This script provides a simple utility to view and analyze CxrruptPad log files.
"""
import os
import sys
import re
import datetime
import argparse
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Fix the import to use the proper module path
from src.utils.logger import get_log_directory

def parse_log_line(line):
    """Parse a log line into timestamp and content."""
    # Expected format: 2023-02-15 14:22:33 [LEVEL] Message
    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.*)', line)
    if match:
        timestamp_str, level, message = match.groups()
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return {
                'timestamp': timestamp,
                'level': level,
                'message': message
            }
        except ValueError:
            pass
    return None

def read_log_file(log_file):
    """Read and parse a log file."""
    log_entries = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = parse_log_line(line.strip())
                if entry:
                    log_entries.append(entry)
    except Exception as e:
        print(f"Error reading log file: {e}")
    return log_entries

def filter_logs(entries, level=None, search_term=None):
    """Filter log entries by level and/or search term."""
    filtered = entries
    
    if level:
        filtered = [entry for entry in filtered if entry['level'] == level.upper()]
    
    if search_term:
        filtered = [entry for entry in filtered 
                   if search_term.lower() in entry['message'].lower()]
    
    return filtered

def display_logs(entries, show_count=None):
    """Display log entries."""
    if not entries:
        print("No log entries found.")
        return
    
    # Display limited number of entries if specified
    if show_count and show_count > 0:
        entries = entries[-show_count:]
    
    for entry in entries:
        timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        level = entry['level']
        message = entry['message']
        
        # Color the output based on log level
        if level == "ERROR" or level == "CRITICAL":
            level_color = "\033[91m"  # Red
        elif level == "WARNING":
            level_color = "\033[93m"  # Yellow
        elif level == "INFO":
            level_color = "\033[92m"  # Green
        else:
            level_color = "\033[0m"   # Default
        
        reset_color = "\033[0m"
        print(f"{timestamp} {level_color}[{level}]{reset_color} {message}")

def analyze_logs(entries):
    """Analyze log entries and print summary."""
    if not entries:
        print("No log entries to analyze.")
        return
    
    # Count entries by level
    level_counts = {}
    for entry in entries:
        level = entry['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    # Find time range
    if entries:
        start_time = min(entry['timestamp'] for entry in entries)
        end_time = max(entry['timestamp'] for entry in entries)
        duration = end_time - start_time
    else:
        start_time = end_time = datetime.datetime.now()
        duration = datetime.timedelta(0)
    
    print("\n=== Log Analysis ===")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print(f"Total Log Entries: {len(entries)}")
    print("\nEntries by Level:")
    for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True):
        percent = (count / len(entries)) * 100
        print(f"  {level}: {count} ({percent:.1f}%)")
    
    if any(entry['level'] in ('ERROR', 'CRITICAL') for entry in entries):
        print("\nErrors and Critical Issues:")
        for entry in entries:
            if entry['level'] in ('ERROR', 'CRITICAL'):
                timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"  {timestamp}: {entry['message']}")

def main():
    parser = argparse.ArgumentParser(description='CxrruptPad Log Viewer')
    parser.add_argument('-f', '--file', help='Specific log file to read (defaults to latest.log)')
    parser.add_argument('-l', '--level', help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('-s', '--search', help='Search term to filter logs')
    parser.add_argument('-n', '--lines', type=int, help='Number of lines to show (from the end)')
    parser.add_argument('-a', '--analyze', action='store_true', help='Analyze logs and show summary')
    parser.add_argument('--list', action='store_true', help='List available log files')
    
    args = parser.parse_args()
    
    log_dir = get_log_directory()
    
    # List available log files
    if args.list:
        print(f"Log directory: {log_dir}")
        log_files = sorted(Path(log_dir).glob('*.log'))
        if log_files:
            print("\nAvailable log files:")
            for log_file in log_files:
                size = os.path.getsize(log_file) / 1024  # Size in KB
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(log_file))
                print(f"  {log_file.name} ({size:.1f} KB, {modified.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print("No log files found.")
        return
    
    # Determine which log file to read
    if args.file:
        log_file = os.path.join(log_dir, args.file)
    else:
        log_file = os.path.join(log_dir, 'latest.log')
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        return
    
    # Read and parse the log file
    entries = read_log_file(log_file)
    
    # Apply filters
    filtered_entries = filter_logs(entries, args.level, args.search)
    
    # Display logs
    print(f"Displaying logs from: {os.path.basename(log_file)}")
    print(f"Total entries: {len(entries)}, Filtered: {len(filtered_entries)}")
    print("-" * 60)
    
    display_logs(filtered_entries, args.lines)
    
    # Analyze logs if requested
    if args.analyze:
        analyze_logs(filtered_entries)

if __name__ == "__main__":
    main() 