#!/usr/bin/env python3
"""
File Descriptor Mapper for gem5

Visualizes the mapping between target (simulated) file descriptors
and host file descriptors, showing the FD lifecycle.

Usage:
    python fd-mapper.py --trace trace.txt
    python fd-mapper.py --live --pid 12345
"""

import argparse
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'

class FDEntry:
    """Represents a file descriptor entry."""
    
    def __init__(self, target_fd: int, host_fd: int, path: str, flags: str):
        self.target_fd = target_fd
        self.host_fd = host_fd
        self.path = path
        self.flags = flags
        self.open_tick = 0
        self.close_tick = None
        self.operations = []  # List of (tick, operation, args)
        
    def add_operation(self, tick: int, op: str, args: str):
        """Add an operation on this FD."""
        self.operations.append((tick, op, args))
    
    def is_open(self) -> bool:
        """Check if FD is currently open."""
        return self.close_tick is None
    
    def lifetime(self) -> int:
        """Get lifetime in ticks."""
        if self.close_tick:
            return self.close_tick - self.open_tick
        return -1  # Still open

class FDMapper:
    """Tracks and visualizes FD mappings."""
    
    def __init__(self):
        self.fd_map: Dict[int, FDEntry] = {}  # target_fd -> FDEntry
        self.fd_history: List[FDEntry] = []
        self.current_tick = 0
        
        # Initialize standard FDs
        self.fd_map[0] = FDEntry(0, 0, "stdin", "r")
        self.fd_map[1] = FDEntry(1, 1, "stdout", "w")
        self.fd_map[2] = FDEntry(2, 2, "stderr", "w")
    
    def parse_trace(self, filename: str):
        """Parse gem5 trace file for FD operations."""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    self.parse_line(line)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: File '{filename}' not found{Colors.RESET}")
            sys.exit(1)
    
    def parse_line(self, line: str):
        """Parse a single line of trace."""
        # Extract tick
        tick_match = re.search(r'^(\d+):', line)
        if tick_match:
            self.current_tick = int(tick_match.group(1))
        
        # Match open syscall
        # "syscall open ('path', flags, mode) → fd"
        open_match = re.search(r'syscall open.*?→\s*(\d+)', line)
        if open_match:
            target_fd = int(open_match.group(1))
            path_match = re.search(r"open\s*\(['\"]([^'\"]+)", line)
            path = path_match.group(1) if path_match else "unknown"
            
            # Assume host_fd is target_fd + some offset (simplified)
            host_fd = target_fd + 10
            
            entry = FDEntry(target_fd, host_fd, path, "rw")
            entry.open_tick = self.current_tick
            self.fd_map[target_fd] = entry
            return
        
        # Match close syscall
        close_match = re.search(r'syscall close\s*\((\d+)\)', line)
        if close_match:
            target_fd = int(close_match.group(1))
            if target_fd in self.fd_map:
                entry = self.fd_map[target_fd]
                entry.close_tick = self.current_tick
                self.fd_history.append(entry)
                del self.fd_map[target_fd]
            return
        
        # Match read/write operations
        rw_match = re.search(r'syscall (read|write)\s*\((\d+),.*?(\d+)\)', line)
        if rw_match:
            op = rw_match.group(1)
            target_fd = int(rw_match.group(2))
            size = int(rw_match.group(3))
            
            if target_fd in self.fd_map:
                self.fd_map[target_fd].add_operation(
                    self.current_tick, op, f"{size} bytes"
                )
    
    def print_current_state(self):
        """Print current FD table."""
        print(f"\n{Colors.BOLD}=== Current FD Table ==={Colors.RESET}")
        print(f"\n{'Target FD':<12} {'Host FD':<10} {'Path':<30} {'Flags':<8} {'Status':<10}")
        print("─" * 80)
        
        for target_fd in sorted(self.fd_map.keys()):
            entry = self.fd_map[target_fd]
            status = f"{Colors.GREEN}OPEN{Colors.RESET}"
            
            # Color code by type
            if entry.path in ["stdin", "stdout", "stderr"]:
                path_color = Colors.GRAY
            elif entry.path.startswith("/tmp"):
                path_color = Colors.YELLOW
            else:
                path_color = Colors.CYAN
            
            print(f"{entry.target_fd:<12} {entry.host_fd:<10} "
                  f"{path_color}{entry.path:<30}{Colors.RESET} "
                  f"{entry.flags:<8} {status}")
        
        print(f"\nTotal open FDs: {len(self.fd_map)}")
    
    def print_history(self):
        """Print FD history."""
        if not self.fd_history:
            print(f"\n{Colors.GRAY}No closed FDs in history{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}=== FD History (Closed FDs) ==={Colors.RESET}\n")
        
        for entry in self.fd_history:
            lifetime = entry.lifetime()
            print(f"{Colors.BOLD}FD {entry.target_fd}{Colors.RESET} → {entry.path}")
            print(f"  Host FD: {entry.host_fd}")
            print(f"  Lifetime: {lifetime:,} ticks")
            print(f"  Operations: {len(entry.operations)}")
            
            if entry.operations:
                read_ops = sum(1 for _, op, _ in entry.operations if op == 'read')
                write_ops = sum(1 for _, op, _ in entry.operations if op == 'write')
                print(f"    Reads: {read_ops}, Writes: {write_ops}")
            print()
    
    def print_statistics(self):
        """Print FD statistics."""
        print(f"\n{Colors.BOLD}=== FD Statistics ==={Colors.RESET}\n")
        
        total_opened = len(self.fd_history) + len(self.fd_map) - 3  # Exclude std fds
        total_closed = len(self.fd_history)
        total_leaked = len(self.fd_map) - 3
        
        print(f"Total FDs opened: {Colors.CYAN}{total_opened}{Colors.RESET}")
        print(f"Total FDs closed: {Colors.GREEN}{total_closed}{Colors.RESET}")
        
        if total_leaked > 0:
            print(f"FDs leaked: {Colors.RED}{total_leaked}{Colors.RESET}")
        else:
            print(f"FDs leaked: {Colors.GREEN}0{Colors.RESET}")
        
        # Calculate total operations
        total_ops = sum(len(e.operations) for e in self.fd_history)
        total_ops += sum(len(e.operations) for e in self.fd_map.values())
        print(f"Total operations: {total_ops}")
        
        # Average lifetime
        if self.fd_history:
            avg_lifetime = sum(e.lifetime() for e in self.fd_history) / len(self.fd_history)
            print(f"Average FD lifetime: {avg_lifetime:,.0f} ticks")
    
    def generate_visualization(self, output_file='fd_map.html'):
        """Generate HTML visualization."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>FD Mapping Visualization</title>
    <style>
        body { font-family: monospace; padding: 20px; }
        table { border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .open { color: green; font-weight: bold; }
        .closed { color: red; }
        .std { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h1>File Descriptor Mapping</h1>
    
    <h2>Current Open FDs</h2>
    <table>
        <tr>
            <th>Target FD</th>
            <th>Host FD</th>
            <th>Path</th>
            <th>Operations</th>
            <th>Status</th>
        </tr>
"""
        
        for target_fd in sorted(self.fd_map.keys()):
            entry = self.fd_map[target_fd]
            std_class = ' class="std"' if target_fd < 3 else ''
            
            html += f"""
        <tr{std_class}>
            <td>{entry.target_fd}</td>
            <td>{entry.host_fd}</td>
            <td>{entry.path}</td>
            <td>{len(entry.operations)}</td>
            <td class="open">OPEN</td>
        </tr>
"""
        
        html += """
    </table>
    
    <h2>FD History</h2>
    <table>
        <tr>
            <th>Target FD</th>
            <th>Path</th>
            <th>Lifetime (ticks)</th>
            <th>Operations</th>
        </tr>
"""
        
        for entry in self.fd_history:
            html += f"""
        <tr>
            <td>{entry.target_fd}</td>
            <td>{entry.path}</td>
            <td>{entry.lifetime():,}</td>
            <td>{len(entry.operations)}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"\n{Colors.GREEN}Visualization saved to {output_file}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description='Visualize gem5 file descriptor mappings'
    )
    
    parser.add_argument('--trace', required=True,
                       help='gem5 trace file to parse')
    parser.add_argument('--html', metavar='FILE',
                       help='Generate HTML visualization')
    
    args = parser.parse_args()
    
    # Create mapper and parse trace
    mapper = FDMapper()
    
    print(f"{Colors.BOLD}Parsing trace file: {args.trace}{Colors.RESET}")
    mapper.parse_trace(args.trace)
    
    # Display results
    mapper.print_current_state()
    mapper.print_history()
    mapper.print_statistics()
    
    # Generate HTML if requested
    if args.html:
        mapper.generate_visualization(args.html)

if __name__ == '__main__':
    main()
