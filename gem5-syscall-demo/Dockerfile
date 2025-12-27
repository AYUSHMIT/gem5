# Dockerfile for gem5 Syscall Demo Environment
FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    m4 \
    scons \
    zlib1g \
    zlib1g-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libprotoc-dev \
    libgoogle-perftools-dev \
    python3 \
    python3-dev \
    python3-pip \
    python-is-python3 \
    doxygen \
    libboost-all-dev \
    libhdf5-serial-dev \
    python3-pydot \
    libpng-dev \
    wget \
    vim \
    gdb \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements
COPY gem5-syscall-demo/requirements.txt /workspace/

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Create convenient aliases
RUN echo 'alias ll="ls -alh"' >> /root/.bashrc && \
    echo 'alias gem5="/workspace/build/X86/gem5.opt"' >> /root/.bashrc

# Set up environment
ENV GEM5_ROOT=/workspace
ENV PATH="${GEM5_ROOT}/build/X86:${PATH}"

# Default command
CMD ["/bin/bash"]

# Build instructions:
# docker build -t gem5-syscall-demo .
#
# Run instructions:
# docker run -it -v $(pwd):/workspace gem5-syscall-demo
#
# To build gem5 inside container:
# scons build/X86/gem5.opt -j$(nproc)
