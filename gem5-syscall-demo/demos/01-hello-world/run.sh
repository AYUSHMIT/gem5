#!/bin/bash
# Convenience wrapper to run the demo with gem5

# Find gem5 binary
GEM5_ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

# Check if gem5 is built
if [ ! -f "$GEM5_BIN" ]; then
    echo "Error: gem5 not found at $GEM5_BIN"
    echo "Please build gem5 first:"
    echo "  cd $GEM5_ROOT"
    echo "  scons build/X86/gem5.opt -j$(nproc)"
    exit 1
fi

# Build the demo if needed
if [ ! -f hello ]; then
    echo "Building demo programs..."
    make || exit 1
fi

# Run with gem5
echo "Running hello world demo with gem5..."
echo ""

$GEM5_BIN run_gem5.py "$@"
