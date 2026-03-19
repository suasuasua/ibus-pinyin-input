#!/bin/bash
# IBus Input Engine Install Script
# Copyright (C) 2026 Tars AI Assistant
# Licensed under LGPL v2.1+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation directories
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr}"
LIBDIR="${INSTALL_PREFIX}/lib"
INCLUDEDIR="${INSTALL_PREFIX}/include"
DATADIR="${INSTALL_PREFIX}/share"

# Engine configuration directories
IBUS_CONF_DIR="${INSTALL_PREFIX}/lib/ibus/engines"
IBUS_DATA_DIR="${DATADIR}/ibus/engines"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IBus Input Engine Installation${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if root or have sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Running as non-root user.${NC}"
    echo -e "${YELLOW}Attempting to use sudo...${NC}"
    SUDO="sudo"
else
    SUDO=""
fi

# Function to print message
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    local missing_deps=0
    
    # Check for required tools
    for cmd in gcc gmake pkg-config; do
        if ! command -v $cmd &> /dev/null; then
            print_error "Required command not found: $cmd"
            missing_deps=1
        fi
    done
    
    if [ $missing_deps -eq 1 ]; then
        print_error "Please install build dependencies first."
        exit 1
    fi
    
    # Check for IBus development packages
    if ! pkg-config --exists ibus; then
        print_warning "IBus development package not found."
        print_info "Please install libibus-dev (Debian/Ubuntu) or libibus-devel (Fedora/CentOS)"
        exit 1
    fi
    
    print_info "All dependencies satisfied."
}

# Function to configure the build
configure_build() {
    echo -e "${BLUE}Configuring build...${NC}"
    
    # Create build directory
    mkdir -p build
    
    cd build
    
    # Run autoreconf to generate Makefile
    $SUDO autoreconf -i
    
    # Configure with options
    $SUDO ./configure \
        --prefix="${INSTALL_PREFIX}" \
        --enable-debug || {
            print_warning "Configure step failed or incomplete."
            exit 1
        }
    
    print_info "Configuration completed."
}

# Function to compile the engine
compile_engine() {
    echo -e "${BLUE}Compiling engine...${NC}"
    
    cd build
    
    $SUDO make -j$(nproc)
    
    if [ $? -ne 0 ]; then
        print_error "Compilation failed!"
        exit 1
    fi
    
    print_info "Compilation successful."
}

# Function to install the engine
install_engine() {
    echo -e "${BLUE}Installing engine...${NC}"
    
    cd build
    
    # Install library and headers
    $SUDO make install
    
    # Install engine configuration files
    if [ -f "${SCRIPT_DIR}/ibus-input-engine.xml" ]; then
        $SUDO mkdir -p "${IBUS_DATA_DIR}"
        $SUDO cp "${SCRIPT_DIR}/ibus-input-engine.xml" "${IBUS_DATA_DIR}/"
        print_info "Engine configuration installed to ${IBUS_DATA_DIR}"
    fi
    
    # Create engine directory if it doesn't exist
    $SUDO mkdir -p "${IBUS_CONF_DIR}"
    
    print_info "Installation completed to ${INSTALL_PREFIX}"
}

# Function to verify installation
verify_installation() {
    echo -e "${BLUE}Verifying installation...${NC}"
    
    # Check if engine is in IBus database
    if [ -f "${IBUS_DATA_DIR}/ibus-input-engine.xml" ]; then
        print_info "✓ Engine configuration file found"
    else
        print_warning "✗ Engine configuration file not found"
    fi
    
    # Check if library is installed
    if [ -f "${LIBDIR}/libmy-input-engine.so" ]; then
        print_info "✓ Engine library installed"
    else
        print_warning "✗ Engine library not found"
    fi
    
    # Check if headers are installed
    if [ -f "${INCLUDEDIR}/ibus-input-engine.h" ]; then
        print_info "✓ Engine headers installed"
    else
        print_warning "✗ Engine headers not found"
    fi
    
    # Check IBus daemon
    if command -v ibus-daemon &> /dev/null; then
        print_info "✓ IBus daemon is available"
        
        # Restart IBus daemon
        print_info "Restarting IBus daemon..."
        $SUDO ibus-daemon --replace
        
        print_info "IBus daemon restarted successfully."
    else
        print_warning "IBus daemon not found. Please install ibus-daemon manually."
    fi
    
    print_info "Installation verification completed."
}

# Function to clean build artifacts
clean_build() {
    echo -e "${BLUE}Cleaning build artifacts...${NC}"
    
    rm -rf build
    print_info "Build directory cleaned."
}

# Main installation function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Installation Wizard${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Parse command line arguments
    case "${1:-}" in
        --clean)
            clean_build
            ;;
        --verify)
            verify_installation
            ;;
        --prefix)
            INSTALL_PREFIX="${2:-${INSTALL_PREFIX}}"
            ;;
        --help|-h)
            show_help
            ;;
        *)
            # Full installation
            check_dependencies
            configure_build
            compile_engine
            install_engine
            verify_installation
            ;;
    esac
}

# Show help
show_help() {
    echo "IBus Input Engine Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean      Clean build directory"
    echo "  --verify     Verify installation"
    echo "  --prefix DIR Install to specified prefix directory"
    echo "  --help, -h   Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  INSTALL_PREFIX  Installation prefix (default: /usr)"
    echo ""
    echo "Examples:"
    echo "  $0              Install to /usr"
    echo "  $0 --prefix /opt/myapp  Install to /opt/myapp"
    echo "  $0 --clean      Clean build directory"
    echo "  $0 --verify     Verify current installation"
}

# Run main function
main "$@"
