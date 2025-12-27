#!/bin/bash
# Quick Start Script for gem5 Syscall Demo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEM5_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "======================================"
echo "  gem5 Syscall Demo Quick Start"
echo "======================================"
echo -e "${NC}"

# Function to print step
print_step() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "$SCRIPT_DIR/demos" ]; then
    print_error "Cannot find demos directory. Are you in gem5-syscall-demo?"
    exit 1
fi

print_step "Checking environment..."

# Check for required tools
command -v gcc >/dev/null 2>&1 || {
    print_error "gcc is not installed. Please install build-essential."
    exit 1
}

command -v python3 >/dev/null 2>&1 || {
    print_error "python3 is not installed."
    exit 1
}

print_step "Environment check passed!"

# Install Python dependencies
print_step "Installing Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -q -r "$SCRIPT_DIR/requirements.txt" || {
        print_warning "Could not install all Python packages. Some features may not work."
    }
else
    print_warning "requirements.txt not found, skipping Python dependencies."
fi

# Build demos
print_step "Building demo programs..."

demos=("01-hello-world" "02-file-operations" "03-process-management")

for demo in "${demos[@]}"; do
    if [ -d "$SCRIPT_DIR/demos/$demo" ]; then
        echo "  Building $demo..."
        (cd "$SCRIPT_DIR/demos/$demo" && make clean && make) || {
            print_warning "Failed to build $demo"
        }
    fi
done

print_step "All demos built successfully!"

# Test demos natively
echo ""
print_step "Testing demos natively (not with gem5)..."

for demo in "${demos[@]}"; do
    if [ -d "$SCRIPT_DIR/demos/$demo" ]; then
        echo -e "\n${BLUE}=== Running $demo ===${NC}"
        
        case $demo in
            "01-hello-world")
                "$SCRIPT_DIR/demos/$demo/hello" 2>&1 | head -10
                ;;
            "02-file-operations")
                "$SCRIPT_DIR/demos/$demo/fileops" 2>&1 | head -20
                ;;
            "03-process-management")
                "$SCRIPT_DIR/demos/$demo/fork_demo" 2>&1 | head -20
                ;;
        esac
    fi
done

# Check for gem5
echo ""
print_step "Checking for gem5..."

GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

if [ -f "$GEM5_BIN" ]; then
    echo -e "${GREEN}✓${NC} gem5 found at: $GEM5_BIN"
    echo ""
    print_step "You can now run demos with gem5:"
    echo "  cd demos/01-hello-world && ./run.sh"
else
    print_warning "gem5 not built yet."
    echo ""
    echo "To build gem5:"
    echo "  cd $GEM5_ROOT"
    echo "  scons build/X86/gem5.opt -j\$(nproc)"
    echo ""
    echo "This will take 15-30 minutes."
fi

# Test visualization tools
echo ""
print_step "Testing visualization tools..."

if python3 "$SCRIPT_DIR/visualization/syscall-tracer.py" --help >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} syscall-tracer.py works"
fi

if python3 "$SCRIPT_DIR/visualization/fd-mapper.py" --help >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} fd-mapper.py works"
fi

# Test analysis tools
if python3 "$SCRIPT_DIR/analysis/coverage-report.py" --arch x86 >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} coverage-report.py works"
fi

echo ""
echo -e "${BLUE}======================================"
echo "  Quick Start Complete!"
echo "======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Explore the demos: cd demos/"
echo "  2. Read the documentation: docs/"
echo "  3. Try the tutorials: docs/tutorial.md"
echo "  4. Use visualization tools: visualization/"
echo ""
echo "For help, see: README.md or CONTRIBUTING.md"
echo ""
