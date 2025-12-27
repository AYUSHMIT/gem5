# 🚀 gem5 Syscall Emulation Demo

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![gem5](https://img.shields.io/badge/gem5-compatible-green.svg)](http://www.gem5.org)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](docs/)
[![Demos](https://img.shields.io/badge/demos-6-orange.svg)](demos/)

> **An interactive, educational showcase of gem5's powerful syscall emulation layer**

This repository provides a comprehensive, hands-on exploration of the gem5 simulator's syscall emulation capabilities. Whether you're a newcomer learning about system simulation or an experienced researcher, you'll find valuable resources, demos, and tools to understand how gem5 emulates system calls.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Demos](#-demos)
- [Visualization Tools](#-visualization-tools)
- [Analysis Tools](#-analysis-tools)
- [Documentation](#-documentation)
- [Interactive Components](#-interactive-components)
- [Contributing](#-contributing)
- [Resources](#-resources)

---

## 🎯 Overview

gem5's **Syscall Emulation (SE)** mode allows simulated programs to make system calls that are handled by the simulator rather than a full operating system. This demo repository showcases:

- **🔍 How syscalls flow** through gem5's emulation layer
- **💻 Practical examples** of common syscalls (I/O, memory, processes, networking)
- **📊 Visualization tools** to see syscall behavior in action
- **📈 Analysis capabilities** for understanding performance and coverage
- **📚 Comprehensive documentation** from beginner to advanced

### Key Features

✨ **6 Complete Demo Programs** covering major syscall categories  
🎨 **Interactive Visualizations** of syscall flows and memory layouts  
📊 **Analysis Tools** for statistics, profiling, and coverage  
📖 **Detailed Documentation** with diagrams and tutorials  
🧪 **Test Suite** for validation and experimentation  
🐳 **Docker Support** for easy setup and reproducibility  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- gem5 simulator (see [gem5 installation guide](http://www.gem5.org/documentation/general_docs/building))
- GCC or Clang compiler
- Optional: Docker for containerized environment

### Installation

```bash
# Clone the repository (if not already in gem5 repo)
git clone https://github.com/AYUSHMIT/gem5.git
cd gem5/gem5-syscall-demo

# Install Python dependencies
pip install -r requirements.txt

# Run a quick demo
cd demos/01-hello-world
python run_demo.py
```

### Running Your First Demo

```bash
# Navigate to the hello world demo
cd demos/01-hello-world

# Compile the example program
make

# Run with gem5 syscall emulation
./run_gem5.sh

# View the syscall trace
python ../../visualization/syscall-tracer.py trace.out
```

---

## 🏗️ Architecture

gem5's syscall emulation layer bridges the gap between simulated programs and the host operating system:

```
┌─────────────────────────────────────────┐
│      Simulated User Program             │
│    (e.g., hello.c compiled binary)      │
└────────────────┬────────────────────────┘
                 │ syscall instruction
                 ▼
┌─────────────────────────────────────────┐
│     gem5 CPU Model (Simulated CPU)      │
│   Detects syscall instruction & traps   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Syscall Descriptor Table           │
│   Maps syscall numbers to handlers      │
│      (syscall_desc.hh/cc)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Syscall Emulation Layer             │
│      (syscall_emul.hh/cc)              │
│  • File descriptor translation          │
│  • Memory address translation           │
│  • Resource management                  │
│  • Host syscall invocation              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Host Operating System              │
│    (actual Linux/macOS/Windows)         │
└─────────────────────────────────────────┘
```

**Key Components:**

- **Process Class** (`process.hh/cc`): Manages simulated process state
- **Syscall Descriptors** (`syscall_desc.hh/cc`): Maps syscall numbers to handlers
- **Emulation Functions** (`syscall_emul.hh/cc`): Implements syscall logic
- **FD Array** (`fd_array.hh/cc`): Translates file descriptors
- **Memory State** (`mem_state.hh/cc`): Manages virtual memory

📖 **[Read detailed architecture documentation](docs/architecture.md)**

---

## 🎬 Demos

Each demo is self-contained with source code, build scripts, and detailed explanations:

### 1. 🌟 [Hello World](demos/01-hello-world/)
**Syscalls:** `write`, `exit`  
**Learning:** Basic syscall flow, stdout handling, process termination

### 2. 📁 [File Operations](demos/02-file-operations/)
**Syscalls:** `open`, `read`, `write`, `close`, `stat`, `mkdir`, `unlink`  
**Learning:** File descriptor management, I/O operations, filesystem interaction

### 3. 🔄 [Process Management](demos/03-process-management/)
**Syscalls:** `fork`, `clone`, `exec`, `wait`, `getpid`  
**Learning:** Process creation, execution, parent-child relationships

### 4. 🧵 [Threading](demos/04-threading/)
**Syscalls:** `futex`, `clone` (with thread flags), `set_tid_address`  
**Learning:** Thread synchronization, futex operations, thread-local storage

### 5. 🌐 [Networking](demos/05-networking/)
**Syscalls:** `socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`  
**Learning:** Socket creation, TCP/UDP communication, network emulation

### 6. 🗺️ [Memory Mapping](demos/06-memory-mapping/)
**Syscalls:** `mmap`, `munmap`, `brk`, `mprotect`  
**Learning:** Virtual memory management, memory protection, dynamic allocation

Each demo includes:
- ✅ Annotated C source code
- ✅ Compilation instructions
- ✅ gem5 run scripts
- ✅ Expected output
- ✅ Detailed explanation of syscall behavior

---

## 🎨 Visualization Tools

Visual tools to understand syscall behavior at runtime:

### 1. **Syscall Tracer** (`visualization/syscall-tracer.py`)
```bash
python visualization/syscall-tracer.py trace.out
```
- Colorized syscall trace output
- Timeline visualization
- Frequency analysis
- Call stack visualization

### 2. **File Descriptor Mapper** (`visualization/fd-mapper.py`)
```bash
python visualization/fd-mapper.py --trace trace.out
```
- Shows target FD → host FD translation
- Tracks FD lifecycle (open → operations → close)
- Visualizes FD inheritance across fork/clone

### 3. **Memory Map Viewer** (`visualization/memory-map-viewer.py`)
```bash
python visualization/memory-map-viewer.py --pid 12345
```
- Displays virtual memory regions
- Shows permissions and mappings
- Tracks mmap/munmap operations

### 4. **Interactive Dashboard** (`visualization/templates/`)
- Web-based real-time monitoring
- D3.js visualizations
- Filterable syscall views

---

## 📊 Analysis Tools

Powerful analysis capabilities for research and debugging:

### 1. **Syscall Statistics** (`analysis/syscall-statistics.py`)
```bash
python analysis/syscall-statistics.py trace.out --output report.html
```
- Syscall frequency distribution
- Performance metrics
- Comparative analysis charts

### 2. **Performance Profiler** (`analysis/performance-profiler.py`)
```bash
python analysis/performance-profiler.py --benchmark program.out
```
- gem5 vs. native execution comparison
- Overhead analysis
- Bottleneck identification

### 3. **Coverage Report** (`analysis/coverage-report.py`)
```bash
python analysis/coverage-report.py --arch x86
```
- Lists implemented syscalls by architecture
- Compatibility matrix (x86, ARM, RISC-V)
- Identifies unimplemented syscalls

---

## 📚 Documentation

Comprehensive guides from beginner to expert:

- **[Architecture Deep Dive](docs/architecture.md)** - System design and components
- **[Syscall Flow Guide](docs/syscall-flow.md)** - Step-by-step syscall execution
- **[Tutorial Series](docs/tutorial.md)** - From zero to hero
- **[API Reference](docs/api-reference.md)** - Function documentation
- **[Debugging Guide](docs/debugging.md)** - Common issues and solutions
- **[Performance Tips](docs/performance.md)** - Optimization strategies

---

## 🎮 Interactive Components

Hands-on exploration tools:

### Jupyter Notebooks (`interactive/jupyter-notebooks/`)
- `01-syscall-basics.ipynb` - Interactive syscall exploration
- `02-fd-management.ipynb` - File descriptor deep dive
- `03-memory-layout.ipynb` - Virtual memory visualization
- `04-performance-analysis.ipynb` - Profiling and metrics

### Web Dashboard (`interactive/web-dashboard/`)
- Real-time syscall monitoring
- Historical analysis
- Configurable views
- Export capabilities

```bash
cd interactive/web-dashboard
python app.py
# Open http://localhost:5000
```

---

## 🧪 Testing

Comprehensive test suite for validation:

```bash
# Run all tests
cd tests
python run_tests.py

# Run specific test category
python run_tests.py --category unit-tests

# Test individual syscall
python run_tests.py --syscall open
```

---

## 🐳 Docker Setup

Quick setup with Docker:

```bash
# Build the container
docker build -t gem5-syscall-demo .

# Run interactive environment
docker run -it -v $(pwd):/workspace gem5-syscall-demo

# Run specific demo
docker run gem5-syscall-demo python demos/01-hello-world/run_demo.py
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas we'd love help with:
- 🆕 New demo programs
- 🐛 Bug fixes and improvements
- 📖 Documentation enhancements
- 🎨 Visualization improvements
- 🧪 Additional test cases

---

## 📚 Resources

### gem5 Documentation
- [Official gem5 Website](http://www.gem5.org)
- [gem5 Documentation](http://www.gem5.org/documentation)
- [Learning gem5](http://www.gem5.org/documentation/learning_gem5/introduction)

### Related Files in gem5
- `src/sim/syscall_emul.hh` - Main syscall emulation header
- `src/sim/syscall_desc.hh` - Syscall descriptor definitions
- `src/sim/process.hh` - Process management
- `src/sim/fd_array.hh` - File descriptor handling

### Community
- [gem5 Users Mailing List](https://www.gem5.org/mailing_lists)
- [gem5 Slack](https://www.gem5.org/join-slack)
- [GitHub Discussions](https://github.com/orgs/gem5/discussions)

---

## 📄 License

This project follows gem5's BSD 3-Clause License. See [LICENSE](../LICENSE) for details.

---

## 🙏 Acknowledgments

This demo repository builds upon the excellent work of the gem5 community. Special thanks to:
- The gem5 development team
- Contributors to the syscall emulation layer
- The broader computer architecture research community

---

## 💡 Pro Tips

> **Did you know?** gem5's syscall emulation can run real binaries without modification! This makes it perfect for architecture exploration without the overhead of full system simulation.

> **Performance Tip:** Use SE mode for workload characterization before running expensive full-system simulations. It's much faster for single-threaded applications.

> **Debugging Tip:** Enable syscall debug flags with `--debug-flags=SyscallVerbose` to see detailed syscall information.

---

<div align="center">

**[⬆ back to top](#-gem5-syscall-emulation-demo)**

Made with ❤️ by the gem5 community

</div>
