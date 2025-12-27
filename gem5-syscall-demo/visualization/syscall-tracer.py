#!/usr/bin/env python3
"""
Syscall Tracer and Visualizer for gem5

This tool traces system calls from gem5 output and generates
colorized, annotated output with statistics and visualizations.

Usage:
    python syscall-tracer.py trace.txt
    python syscall-tracer.py --live m5out/debug.trace
    python syscall-tracer.py --stats trace.txt
"""

import argparse
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple
import json

# Color codes for terminal output
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

# Syscall categories for colorization
SYSCALL_COLORS = {
    'file': Colors.GREEN,      # open, close, read, write
    'process': Colors.BLUE,    # fork, clone, exec
    'memory': Colors.MAGENTA,  # mmap, munmap, brk
    'network': Colors.CYAN,    # socket, bind, connect
    'thread': Colors.YELLOW,   # futex, clone
    'info': Colors.GRAY,       # getpid, stat
}

SYSCALL_CATEGORIES = {
    'open': 'file', 'close': 'file', 'read': 'file', 'write': 'file',
    'stat': 'file', 'fstat': 'file', 'lstat': 'file',
    'access': 'file', 'mkdir': 'file', 'rmdir': 'file',
    'fork': 'process', 'clone': 'process', 'exec': 'process',
    'wait': 'process', 'exit': 'process', 'exit_group': 'process',
    'mmap': 'memory', 'munmap': 'memory', 'brk': 'memory',
    'mprotect': 'memory', 'mremap': 'memory',
    'socket': 'network', 'bind': 'network', 'connect': 'network',
    'accept': 'network', 'listen': 'network', 'send': 'network', 'recv': 'network',
    'futex': 'thread', 'set_tid_address': 'thread',
    'getpid': 'info', 'getuid': 'info', 'gettid': 'info',
}

class SyscallEntry:
    """Represents a single syscall entry."""
    
    def __init__(self, tick, cpu, name, args, result=None):
        self.tick = int(tick)
        self.cpu = cpu
        self.name = name
        self.args = args
        self.result = result
        self.category = SYSCALL_CATEGORIES.get(name, 'info')
        
    def get_color(self):
        """Get color for this syscall category."""
        return SYSCALL_COLORS.get(self.category, Colors.RESET)
    
    def format_args(self):
        """Format arguments nicely."""
        if not self.args:
            return "()"
        return f"({', '.join(str(arg) for arg in self.args)})"
    
    def format_result(self):
        """Format return value."""
        if self.result is None:
            return ""
        
        # Check for errors (negative values)
        if isinstance(self.result, int) and self.result < 0:
            return f"{Colors.RED}→ {self.result}{Colors.RESET}"
        else:
            return f"{Colors.GREEN}→ {self.result}{Colors.RESET}"
    
    def __str__(self):
        color = self.get_color()
        formatted = f"{Colors.GRAY}{self.tick:>12}{Colors.RESET} "
        formatted += f"{Colors.BOLD}{color}{self.name}{Colors.RESET}"
        formatted += f"{self.format_args()} "
        formatted += self.format_result()
        return formatted

class SyscallTracer:
    """Traces and analyzes syscalls from gem5 output."""
    
    def __init__(self):
        self.syscalls: List[SyscallEntry] = []
        self.stats = {
            'total_calls': 0,
            'by_name': Counter(),
            'by_category': Counter(),
            'errors': Counter(),
            'timeline': [],
        }
        
    def parse_line(self, line: str) -> SyscallEntry:
        """Parse a single line of gem5 syscall trace."""
        # Example formats:
        # "      0: system.cpu T0 : @main : syscall write (1, 0x401234, 37)"
        # "      0: Syscall write returned 37"
        
        # Match syscall invocation
        match = re.search(r'(\d+):\s+.*?syscall\s+(\w+)\s*\((.*?)\)', line)
        if match:
            tick = match.group(1)
            name = match.group(2)
            args_str = match.group(3)
            args = [arg.strip() for arg in args_str.split(',')] if args_str else []
            return SyscallEntry(tick, 'cpu0', name, args)
        
        # Match syscall return
        match = re.search(r'(\d+):\s+.*?returned\s+(-?\d+)', line)
        if match and self.syscalls:
            result = int(match.group(2))
            self.syscalls[-1].result = result
            
        return None
    
    def trace_file(self, filename: str):
        """Parse syscalls from a trace file."""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    entry = self.parse_line(line)
                    if entry:
                        self.syscalls.append(entry)
                        self.update_stats(entry)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: File '{filename}' not found{Colors.RESET}")
            sys.exit(1)
    
    def update_stats(self, entry: SyscallEntry):
        """Update statistics with new syscall."""
        self.stats['total_calls'] += 1
        self.stats['by_name'][entry.name] += 1
        self.stats['by_category'][entry.category] += 1
        
        if entry.result and isinstance(entry.result, int) and entry.result < 0:
            self.stats['errors'][entry.name] += 1
        
        self.stats['timeline'].append((entry.tick, entry.name))
    
    def print_trace(self, limit=None):
        """Print colorized trace output."""
        print(f"\n{Colors.BOLD}=== Syscall Trace ==={Colors.RESET}\n")
        
        syscalls = self.syscalls[:limit] if limit else self.syscalls
        for entry in syscalls:
            print(entry)
        
        if limit and len(self.syscalls) > limit:
            print(f"\n{Colors.GRAY}... ({len(self.syscalls) - limit} more calls){Colors.RESET}")
    
    def print_statistics(self):
        """Print syscall statistics."""
        print(f"\n{Colors.BOLD}=== Syscall Statistics ==={Colors.RESET}\n")
        
        print(f"Total syscalls: {Colors.CYAN}{self.stats['total_calls']}{Colors.RESET}")
        print(f"Unique syscalls: {Colors.CYAN}{len(self.stats['by_name'])}{Colors.RESET}")
        print(f"Total errors: {Colors.RED}{sum(self.stats['errors'].values())}{Colors.RESET}")
        
        # By name
        print(f"\n{Colors.BOLD}Top Syscalls:{Colors.RESET}")
        for name, count in self.stats['by_name'].most_common(10):
            category = SYSCALL_CATEGORIES.get(name, 'info')
            color = SYSCALL_COLORS.get(category, Colors.RESET)
            pct = (count / self.stats['total_calls']) * 100
            bar = '█' * int(pct / 2)
            print(f"  {color}{name:20}{Colors.RESET} {count:>6} ({pct:>5.1f}%) {bar}")
        
        # By category
        print(f"\n{Colors.BOLD}By Category:{Colors.RESET}")
        for category, count in self.stats['by_category'].most_common():
            color = SYSCALL_COLORS.get(category, Colors.RESET)
            pct = (count / self.stats['total_calls']) * 100
            bar = '█' * int(pct / 2)
            print(f"  {color}{category:20}{Colors.RESET} {count:>6} ({pct:>5.1f}%) {bar}")
        
        # Errors
        if self.stats['errors']:
            print(f"\n{Colors.BOLD}Errors:{Colors.RESET}")
            for name, count in self.stats['errors'].most_common():
                print(f"  {Colors.RED}{name:20}{Colors.RESET} {count:>6} errors")
    
    def generate_timeline_html(self, output_file='timeline.html'):
        """Generate HTML visualization of syscall timeline."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Syscall Timeline</title>
    <style>
        body { font-family: monospace; padding: 20px; }
        .timeline { margin: 20px 0; }
        .syscall {
            display: inline-block;
            padding: 2px 5px;
            margin: 2px;
            border-radius: 3px;
            font-size: 10px;
        }
        .file { background-color: #90EE90; }
        .process { background-color: #87CEEB; }
        .memory { background-color: #DDA0DD; }
        .network { background-color: #00CED1; }
        .thread { background-color: #FFD700; }
        .info { background-color: #D3D3D3; }
    </style>
</head>
<body>
    <h1>Syscall Timeline Visualization</h1>
    <div class="timeline">
"""
        
        for tick, name in self.stats['timeline']:
            category = SYSCALL_CATEGORIES.get(name, 'info')
            html += f'        <span class="syscall {category}" title="Tick {tick}">{name}</span>\n'
        
        html += """
    </div>
    <h2>Legend</h2>
    <div>
        <span class="syscall file">file I/O</span>
        <span class="syscall process">process</span>
        <span class="syscall memory">memory</span>
        <span class="syscall network">network</span>
        <span class="syscall thread">threading</span>
        <span class="syscall info">info/other</span>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"\n{Colors.GREEN}Timeline saved to {output_file}{Colors.RESET}")
    
    def export_json(self, output_file='syscalls.json'):
        """Export syscalls to JSON format."""
        data = {
            'syscalls': [
                {
                    'tick': s.tick,
                    'name': s.name,
                    'args': s.args,
                    'result': s.result,
                    'category': s.category,
                }
                for s in self.syscalls
            ],
            'stats': {
                'total': self.stats['total_calls'],
                'by_name': dict(self.stats['by_name']),
                'by_category': dict(self.stats['by_category']),
                'errors': dict(self.stats['errors']),
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n{Colors.GREEN}Data exported to {output_file}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description='Trace and visualize gem5 syscalls',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s trace.txt                    # Show colorized trace
  %(prog)s --stats trace.txt            # Show statistics
  %(prog)s --html timeline.html trace.txt  # Generate HTML visualization
  %(prog)s --json output.json trace.txt # Export to JSON
        """
    )
    
    parser.add_argument('trace_file', help='gem5 trace file to parse')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics instead of trace')
    parser.add_argument('--html', metavar='FILE',
                       help='Generate HTML timeline visualization')
    parser.add_argument('--json', metavar='FILE',
                       help='Export data to JSON')
    parser.add_argument('--limit', type=int, metavar='N',
                       help='Limit trace output to N entries')
    
    args = parser.parse_args()
    
    # Create tracer and parse file
    tracer = SyscallTracer()
    
    print(f"{Colors.BOLD}Parsing trace file: {args.trace_file}{Colors.RESET}")
    tracer.trace_file(args.trace_file)
    print(f"{Colors.GREEN}Parsed {len(tracer.syscalls)} syscall entries{Colors.RESET}")
    
    # Output results
    if args.stats:
        tracer.print_statistics()
    else:
        tracer.print_trace(limit=args.limit)
        tracer.print_statistics()
    
    # Generate HTML if requested
    if args.html:
        tracer.generate_timeline_html(args.html)
    
    # Export JSON if requested
    if args.json:
        tracer.export_json(args.json)

if __name__ == '__main__':
    main()
