# Contributing to gem5 Syscall Demo

Thank you for your interest in contributing! This document provides guidelines for contributing to this educational demo repository.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

This project follows the [gem5 Code of Conduct](../CODE-OF-CONDUCT.md). Please read it before contributing.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide clear description and reproduction steps
- Include gem5 version and system information
- Add relevant logs or error messages

### Suggesting Enhancements

- Describe the enhancement clearly
- Explain the motivation and use cases
- Consider backwards compatibility

### Contributing Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Setup

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install build-essential git python3 python3-pip

# Install Python dependencies
pip3 install -r gem5-syscall-demo/requirements.txt
```

### Using Docker

```bash
# Build container
cd gem5-syscall-demo
docker build -t gem5-demo .

# Run container
docker run -it -v $(pwd)/..:/workspace gem5-demo

# Inside container, build gem5
scons build/X86/gem5.opt -j$(nproc)
```

### Local Development

```bash
# Clone repository
git clone https://github.com/AYUSHMIT/gem5.git
cd gem5

# Build gem5
scons build/X86/gem5.opt -j$(nproc)

# Test a demo
cd gem5-syscall-demo/demos/01-hello-world
make
./run.sh
```

## Coding Standards

### C/C++ Code

- Follow gem5 coding style
- Use meaningful variable names
- Add comments for complex logic
- Include error handling
- Test edge cases

**Example:**

```c
// Good
int fd = open(path, O_RDONLY);
if (fd < 0) {
    perror("open");
    return -1;
}

// Avoid
int f = open(p, 0);  // No error check, unclear names
```

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions
- Handle exceptions gracefully

**Example:**

```python
def parse_trace(filename: str) -> List[SyscallEntry]:
    """
    Parse syscall trace from gem5 output.
    
    Args:
        filename: Path to trace file
        
    Returns:
        List of parsed syscall entries
        
    Raises:
        FileNotFoundError: If trace file doesn't exist
    """
    try:
        with open(filename, 'r') as f:
            return [parse_line(line) for line in f]
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        raise
```

### Documentation

- Use Markdown for documentation
- Include code examples
- Add diagrams where helpful
- Keep language clear and educational

**Markdown Style:**

```markdown
# Main Heading

## Section

### Subsection

**Bold for emphasis**
*Italic for terms*
`Code inline`

## Code Blocks

## bash
command here
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update README.md if adding features
   - Add docstrings to new functions
   - Update relevant tutorials

2. **Test Your Changes**
   - Run existing demos to ensure no breakage
   - Test new features thoroughly
   - Include test cases if applicable

3. **Commit Messages**
   - Use clear, descriptive messages
   - Reference issue numbers
   - Follow format: `[category] Brief description`

**Example commits:**

```
[demo] Add process management demo
[viz] Improve syscall tracer performance
[docs] Update API reference for new functions
[fix] Correct FD mapping in visualization
```

4. **Create Pull Request**
   - Clear title describing change
   - Detailed description of what and why
   - Reference related issues
   - Include screenshots for UI changes

### Review Process

- Maintainers will review your PR
- Address feedback constructively
- Make requested changes
- Once approved, PR will be merged

## Areas for Contribution

### 🆕 New Demos

We welcome new demo programs! Good candidates:

- **Network Programming**: Socket demos with client/server
- **Signal Handling**: Signal syscall demonstrations
- **Advanced IPC**: Message queues, semaphores, shared memory
- **Performance**: Benchmarking different syscall patterns

**Template for new demo:**

```
demos/XX-demo-name/
├── README.md          # Comprehensive explanation
├── demo.c             # Main demo program
├── Makefile           # Build script
├── run_gem5.py        # gem5 configuration
└── run.sh             # Convenience wrapper
```

### 📊 Visualization Tools

Ideas for new visualizations:

- **Call Graph**: Visualize syscall dependencies
- **Timeline**: Interactive timeline of syscall execution
- **Heat Map**: Show syscall hotspots
- **Comparison**: Side-by-side gem5 vs native

### 📖 Documentation

Always appreciated:

- Tutorial improvements
- More code examples
- Troubleshooting guides
- Performance tips
- Video tutorials

### 🧪 Testing

Help improve reliability:

- Add test cases for demos
- Create regression tests
- Test on different architectures
- Test edge cases and error conditions

### 🎨 Web Interface

Enhance the web dashboard:

- Real-time monitoring improvements
- Better visualizations
- Export capabilities
- Filtering and search

## Style Guidelines

### Educational Tone

This is an educational project. Keep content:

- **Clear**: Avoid jargon, explain concepts
- **Comprehensive**: Provide context and examples
- **Engaging**: Use emojis, callouts, diagrams
- **Progressive**: Build from simple to complex

### Code Comments

```c
// Good: Explains why
// Allocate FD because we need to track host->target mapping
int target_fd = allocate_fd(host_fd);

// Too brief: States obvious
// Allocate FD
int target_fd = allocate_fd(host_fd);

// Too verbose: Unnecessary detail
// This function allocates a file descriptor by calling the
// allocate_fd function which takes a host file descriptor
// as input and returns a target file descriptor that will
// be used by the simulated program...
```

### Documentation Comments

Use this format for major sections:

```markdown
## Feature Name

### Overview
Brief description of what this is.

### Usage
How to use it with examples.

### Technical Details
How it works internally.

### Common Issues
Known problems and solutions.
```

## Getting Help

If you need help contributing:

- 💬 [GitHub Discussions](https://github.com/orgs/gem5/discussions)
- 💡 [gem5 Slack](https://www.gem5.org/join-slack)
- 📧 [Mailing Lists](https://www.gem5.org/mailing_lists)
- 📚 [gem5 Documentation](http://www.gem5.org/documentation)

## Recognition

Contributors will be:

- Listed in commit history
- Acknowledged in release notes
- Credited in documentation

Thank you for contributing to make gem5 more accessible and educational!

---

**Questions?** Open an issue or reach out on Slack!
