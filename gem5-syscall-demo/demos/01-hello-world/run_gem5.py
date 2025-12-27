#!/usr/bin/env python3
"""
gem5 Configuration Script for Hello World Demo

This script sets up a minimal gem5 simulation to run the hello world
program in syscall emulation mode.
"""

import argparse
import sys
import os

# Add gem5 to Python path
gem5_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(gem5_root, 'configs'))

import m5
from m5.objects import *

def create_system():
    """Create a simple system with one CPU."""
    
    # Create the system
    system = System()
    
    # Set up clock domain
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '1GHz'
    system.clk_domain.voltage_domain = VoltageDomain()
    
    # Set up memory
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('512MB')]
    
    # Create a simple CPU (Atomic for speed)
    system.cpu = AtomicSimpleCPU()
    
    # Create memory bus
    system.membus = SystemXBar()
    
    # Connect CPU to memory bus
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports
    
    # Create interrupt controller
    system.cpu.createInterruptController()
    
    # Create memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports
    
    # Connect system port
    system.system_port = system.membus.cpu_side_ports
    
    return system

def main():
    parser = argparse.ArgumentParser(description='Run hello world in gem5')
    parser.add_argument('binary', nargs='?', default='hello',
                       help='Binary to execute (default: hello)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable syscall debug output')
    args = parser.parse_args()
    
    # Check if binary exists
    if not os.path.exists(args.binary):
        print(f"Error: Binary '{args.binary}' not found!")
        print("Run 'make' first to build the demo programs.")
        sys.exit(1)
    
    # Create the system
    system = create_system()
    
    # Set up the workload
    system.workload = SEWorkload.init_compatible(args.binary)
    
    # Create the process
    process = Process()
    process.cmd = [args.binary]
    system.cpu.workload = process
    system.cpu.createThreads()
    
    # Instantiate the system
    root = Root(full_system=False, system=system)
    m5.instantiate()
    
    # Enable debug flags if requested
    if args.debug:
        m5.debug.flags['Syscall'].enable()
        m5.debug.flags['SyscallVerbose'].enable()
    
    print(f"Beginning simulation of {args.binary}")
    print("=" * 60)
    
    # Run the simulation
    exit_event = m5.simulate()
    
    print("=" * 60)
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

if __name__ == '__main__':
    main()
