#!/bin/bash
# IBus Input Engine Uninstall Script
# Copyright (C) 2026 Tars AI Assistant
# Licensed under LGPL v2.1+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default installation directories
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr}"
LIBDIR="${INSTALL_PREFIX}/lib"
INCLUDEDIR="${INSTALL_PREFIX}/include"
DATADIR="${INSTALL_PREFIX}/share"

IBUS_CONF_DIR="${INSTALL_PREFIX}/lib/ibus/engines"
IBUS_DATA_DIR="${DATADIR}/ibus/engines"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IBus Input Engine Uninstall${NC}"
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

# Function to uninstall engine
uninstall_engine() {
    echo -e "${BLUE}Uninstalling IBus input engine...${NC}"
    
    # Remove engine configuration file
    ENGINE_XML="${IBUS_DATA_DIR}/ibus-input-engine.xml"
    if [ -f "$ENGINE_XML" ]; then
        $SUDO rm -f "$ENGINE_XML"
        print_info "Removed engine configuration: $ENGINE_XML"
    else
        print_warning "Engine configuration not found at: $ENGINE_XML"
    fi
    
    # Remove engine directory if empty
    if [ -d "$IBUS_DATA_DIR" ]; then
        $SUDO rm -rf "$IBUS_DATA_DIR"
        print_info "Removed engine data directory: $IBUS_DATA_DIR"
    fi
    
    # Remove engine directory if it exists
    if [ -d "$IBUS_CONF_DIR" ]; then
        $SUDO rm -rf "$IBUS_CONF_DIR"
        print_info "Removed engine configuration directory: $IBUS_CONF_DIR"
    fi
    
    # Remove library (if in lib directory)
    LIB_FILE="${LIBDIR}/libmy-input-engine.so"
    if [ -f "$LIB_FILE" ]; then
        $SUDO rm -f "$LIB_FILE"
        print_info "Removed engine library: $LIB_FILE"
    else
        print_warning "Engine library not found at: $LIB_FILE"
    fi
    
    # Remove headers (if in include directory)
    HEADER_FILE="${INCLUDEDIR}/ibus-input-engine.h"
    if [ -f "$HEADER_FILE" ]; then
        $SUDO rm -f "$HEADER_FILE"
        print_info "Removed engine header: $HEADER_FILE"
    else
        print_warning "Engine header not found at: $HEADER_FILE"
    fi
    
    # Remove all engine-related files
    $SUDO find "$INSTALL_PREFIX" -name "*my-input-engine*" -type f 2>/dev/null | while read file; do
        $SUDO rm -f "$file"
        print_info "Removed: $file"
    done
    
    print_info "Engine files uninstalled."
}

# Function to restart IBus daemon
restart_ibus_daemon() {
    echo -e "${BLUE}Restarting IBus daemon...${NC}"
    
    if command -v ibus-daemon &> /dev/null; then
        print_info "Stopping IBus daemon..."
        $SUDO ibus-daemon --exit
        
        print_info "Starting IBus daemon..."
        $SUDO ibus-daemon --replace
        
        print_info "IBus daemon restarted successfully."
    else
        print_warning "IBus daemon not found. Skipping restart."
    fi
}

# Function to remove from gsettings
remove_from_gsettings() {
    echo -e "${BLUE}Removing from IBus settings...${NC}"
    
    # Remove engine from default input method
    if command -v gsettings &> /dev/null; then
        # Get the schema path
        SCHEMA_PATH=$(gsettings list-schemas | grep -i ibus || true)
        
        if [ -n "$SCHEMA_PATH" ]; then
            print_info "Checking IBus settings..."
            
            # Remove from default input method
            $SUDO gsettings reset -s org.freedesktop.ibus.settings.inputmethod default-input-method || true
            
            # Remove from enabled engines list if exists
            $SUDO gsettings reset -s org.freedesktop.ibus.settings.inputmethod enabled-engines || true
            
            print_info "IBus settings cleaned."
        fi
    else
        print_warning "gsettings not available. Skipping settings removal."
    fi
}

# Function to clean up build artifacts
clean_build() {
    echo -e "${BLUE}Cleaning build artifacts...${NC}"
    
    # Remove build directory if it exists
    if [ -d "build" ]; then
        rm -rf build
        print_info "Removed build directory."
    fi
    
    # Remove any installed engine files
    find "$INSTALL_PREFIX" -name "*my-input-engine*" -type f 2>/dev/null | while read file; do
        $SUDO rm -f "$file"
    done
    
    print_info "Build artifacts cleaned."
}

# Function to verify uninstallation
verify_uninstallation() {
    echo -e "${BLUE}Verifying uninstallation...${NC}"
    
    local success=0
    
    # Check if engine configuration exists
    if [ -f "${IBUS_DATA_DIR}/ibus-input-engine.xml" ]; then
        print_warning "✗ Engine configuration still exists"
        success=1
    else
        print_info "✓ Engine configuration removed"
    fi
    
    # Check if library exists
    if [ -f "${LIBDIR}/libmy-input-engine.so" ]; then
        print_warning "✗ Engine library still exists"
        success=1
    else
        print_info "✓ Engine library removed"
    fi
    
    # Check if headers exist
    if [ -f "${INCLUDEDIR}/ibus-input-engine.h" ]; then
        print_warning "✗ Engine headers still exist"
        success=1
    else
        print_info "✓ Engine headers removed"
    fi
    
    if [ $success -eq 0 ]; then
        print_info "Uninstallation verified successfully."
    else
        print_warning "Some files may still exist."
    fi
}

# Function to show help
show_help() {
    echo "IBus Input Engine Uninstall Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h   Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  INSTALL_PREFIX  Installation prefix (default: /usr)"
    echo ""
    echo "Examples:"
    echo "  $0              Uninstall engine"
    echo "  $0 --help      Show help message"
}

# Main uninstall function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Uninstall Wizard${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Parse command line arguments
    case "${1:-}" in
        --clean)
            clean_build
            ;;
        --verify)
            verify_uninstallation
            ;;
        --help|-h)
            show_help
            ;;
        *)
            # Full uninstallation
            uninstall_engine
            remove_from_gsettings
            restart_ibus_daemon
            clean_build
            verify_uninstallation
            ;;
    esac
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  Uninstall completed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    print_info "You may need to log out and log back in for changes to take effect."
}

# Run main function
main "$@"
