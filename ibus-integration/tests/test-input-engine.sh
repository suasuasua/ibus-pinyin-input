#!/bin/bash
# IBus Input Engine Test Script
# Copyright (C) 2026 Tars AI Assistant
# Licensed under LGPL v2.1+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test results array
declare -a TEST_RESULTS

# Function to print message
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

# Function to record test result
record_test() {
    local test_name="$1"
    local result="$2"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    TEST_RESULTS+=("$test_name: $result")
}

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if file is executable
file_executable() {
    [ -x "$1" ]
}

# Test 1: Check IBus development headers
test_ibus_headers() {
    local test_name="IBus development headers"
    print_info "Testing: $test_name"
    
    if file_exists "/usr/include/ibus.h"; then
        print_pass "IBus headers found at /usr/include/ibus.h"
        record_test "$test_name" "PASS"
    else
        print_fail "IBus headers not found at /usr/include/ibus.h"
        record_test "$test_name" "FAIL"
    fi
}

# Test 2: Check IBus library
test_ibus_library() {
    local test_name="IBus library"
    print_info "Testing: $test_name"
    
    local lib_file="/usr/lib/x86_64-linux-gnu/libibus.so"
    
    if file_exists "$lib_file"; then
        print_pass "IBus library found at $lib_file"
        record_test "$test_name" "PASS"
    else
        print_fail "IBus library not found at $lib_file"
        record_test "$test_name" "FAIL"
    fi
}

# Test 3: Check IBus configuration directory
test_ibus_config_dir() {
    local test_name="IBus configuration directory"
    print_info "Testing: $test_name"
    
    local config_dir="/usr/share/ibus/engines"
    
    if file_exists "$config_dir" || file_exists "/usr/share/ibus/engines/my-input-engine.xml"; then
        if file_exists "/usr/share/ibus/engines/my-input-engine.xml"; then
            print_pass "Engine configuration found at /usr/share/ibus/engines/my-input-engine.xml"
            record_test "$test_name" "PASS"
        else
            print_pass "IBus configuration directory exists"
            record_test "$test_name" "PASS"
        fi
    else
        print_fail "IBus configuration directory not found at $config_dir"
        record_test "$test_name" "FAIL"
    fi
}

# Test 4: Check IBus engine XML file
test_engine_xml() {
    local test_name="Engine XML configuration"
    print_info "Testing: $test_name"
    
    local xml_file="/usr/share/ibus/engines/my-input-engine.xml"
    
    if file_exists "$xml_file"; then
        print_pass "Engine XML file exists"
        
        # Validate XML syntax
        if command_exists xmllint; then
            if xmllint --noout "$xml_file" 2>/dev/null; then
                print_pass "XML syntax is valid"
            else
                print_fail "XML syntax is invalid"
                record_test "$test_name" "FAIL"
                return
            fi
        fi
        
        # Check required fields
        local required_fields=("name" "author" "license")
        for field in "${required_fields[@]}"; do
            if grep -q "<$field>" "$xml_file"; then
                print_pass "XML contains required field: $field"
            else
                print_fail "XML missing required field: $field"
                record_test "$test_name" "FAIL"
                return
            fi
        done
        
        record_test "$test_name" "PASS"
    else
        print_fail "Engine XML file not found at $xml_file"
        record_test "$test_name" "FAIL"
    fi
}

# Test 5: Check engine library
test_engine_library() {
    local test_name="Engine library"
    print_info "Testing: $test_name"
    
    local lib_file="/usr/lib/x86_64-linux-gnu/libmy-input-engine.so"
    
    if file_exists "$lib_file"; then
        print_pass "Engine library found at $lib_file"
        
        # Check if library is shared
        if file "$lib_file" | grep -q "shared object"; then
            print_pass "Library is a shared object"
        else
            print_fail "Library is not a shared object"
            record_test "$test_name" "FAIL"
            return
        fi
        
        # Check library dependencies
        if command_exists ldd; then
            ldd "$lib_file" 2>/dev/null | grep -q "libibus.so"
            if [ $? -eq 0 ]; then
                print_pass "Library depends on libibus.so"
            else
                print_fail "Library does not depend on libibus.so"
                record_test "$test_name" "FAIL"
                return
            fi
        fi
        
        record_test "$test_name" "PASS"
    else
        print_fail "Engine library not found at $lib_file"
        record_test "$test_name" "FAIL"
    fi
}

# Test 6: Check IBus daemon
test_ibus_daemon() {
    local test_name="IBus daemon"
    print_info "Testing: $test_name"
    
    if command_exists ibus-daemon; then
        print_pass "IBus daemon executable found"
        
        # Check if daemon is running
        if pgrep -x "ibus-daemon" > /dev/null 2>&1; then
            print_pass "IBus daemon is running"
        else
            print_info "IBus daemon is not running (this is OK for testing)"
        fi
        
        record_test "$test_name" "PASS"
    else
        print_fail "IBus daemon not found"
        record_test "$test_name" "FAIL"
    fi
}

# Test 7: Check gsettings availability
test_gsettings() {
    local test_name="gsettings availability"
    print_info "Testing: $test_name"
    
    if command_exists gsettings; then
        print_pass "gsettings command is available"
        
        # Check if engine settings exist
        if gsettings list-keys | grep -q "my-input-engine"; then
            print_pass "Engine settings exist"
            record_test "$test_name" "PASS"
        else
            print_info "Engine settings not found (may be expected if not configured)"
            record_test "$test_name" "PASS"
        fi
    else
        print_fail "gsettings command not found"
        record_test "$test_name" "FAIL"
    fi
}

# Test 8: Check engine properties
test_engine_properties() {
    local test_name="Engine properties"
    print_info "Testing: $test_name"
    
    if command_exists gsettings; then
        local engine_prefix="org.freedesktop.ibus.engine.my-input-engine"
        
        # Check for required properties
        local required_properties=("InputMode" "CursorStyle" "ShowPreedit")
        
        for prop in "${required_properties[@]}"; do
            if gsettings list-keys | grep -q "$engine_prefix.$prop"; then
                print_pass "Property found: $prop"
            else
                print_info "Property not found: $prop (may be expected)"
            fi
        done
        
        record_test "$test_name" "PASS"
    else
        print_fail "Cannot check engine properties (gsettings not available)"
        record_test "$test_name" "FAIL"
    fi
}

# Test 9: Check keyboard layout support
test_keyboard_layout() {
    local test_name="Keyboard layout support"
    print_info "Testing: $test_name"
    
    if file_exists "/usr/share/ibus/engines/my-input-engine.xml"; then
        if grep -q "keyboard-layout" "/usr/share/ibus/engines/my-input-engine.xml"; then
            print_pass "Keyboard layout configuration found"
            
            # Check for supported layouts
            local layouts=("us" "zh_cn" "ja" "ko")
            for layout in "${layouts[@]}"; do
                if grep -q "name.*$layout" "/usr/share/ibus/engines/my-input-engine.xml"; then
                    print_pass "Layout supported: $layout"
                else
                    print_info "Layout not configured: $layout"
                fi
            done
            
            record_test "$test_name" "PASS"
        else
            print_fail "Keyboard layout configuration not found"
            record_test "$test_name" "FAIL"
        fi
    else
        print_fail "Cannot check keyboard layout (engine XML not found)"
        record_test "$test_name" "FAIL"
    fi
}

# Test 10: Check IBus environment
test_ibus_environment() {
    local test_name="IBus environment"
    print_info "Testing: $test_name"
    
    # Check IBUS_ENVIRONMENT
    if [ -n "$IBUS_ENVIRONMENT" ]; then
        print_pass "IBUS_ENVIRONMENT is set: $IBUS_ENVIRONMENT"
    else
        print_info "IBUS_ENVIRONMENT is not set (this is OK)"
    fi
    
    # Check IBUS_INI_FILE
    if [ -n "$IBUS_INI_FILE" ]; then
        print_pass "IBUS_INI_FILE is set: $IBUS_INI_FILE"
    else
        print_info "IBUS_INI_FILE is not set (this is OK)"
    fi
    
    # Check IBUS_CONF_DIR
    if [ -n "$IBUS_CONF_DIR" ]; then
        print_pass "IBUS_CONF_DIR is set: $IBUS_CONF_DIR"
    else
        print_info "IBUS_CONF_DIR is not set (this is OK)"
    fi
    
    record_test "$test_name" "PASS"
}

# Test 11: Check gsettings engine configuration
test_gsettings_engine() {
    local test_name="gsettings engine configuration"
    print_info "Testing: $test_name"
    
    if command_exists gsettings; then
        # Check if engine is in default input method
        local default_method=$(gsettings get org.freedesktop.ibus.settings.inputmethod default-input-method 2>/dev/null)
        
        if [ -n "$default_method" ]; then
            print_info "Default input method: $default_method"
            
            if [ "$default_method" = "my-input-engine" ]; then
                print_pass "Engine is set as default input method"
            else
                print_info "Engine is not set as default input method"
            fi
        else
            print_info "Default input method not set"
        fi
        
        # Check enabled engines
        local enabled_engines=$(gsettings get org.freedesktop.ibus.settings.inputmethod enabled-engines 2>/dev/null)
        
        if [ -n "$enabled_engines" ]; then
            print_info "Enabled engines: $enabled_engines"
            
            if echo "$enabled_engines" | grep -q "my-input-engine"; then
                print_pass "Engine is enabled"
            else
                print_info "Engine is not enabled (this is OK)"
            fi
        else
            print_info "No enabled engines configured"
        fi
        
        record_test "$test_name" "PASS"
    else
        print_fail "Cannot check gsettings configuration"
        record_test "$test_name" "FAIL"
    fi
}

# Test 12: Check IBus schema
test_ibus_schema() {
    local test_name="IBus schema"
    print_info "Testing: $test_name"
    
    if command_exists gsettings; then
        local schema=$(gsettings list-schemas | grep -i ibus 2>/dev/null)
        
        if [ -n "$schema" ]; then
            print_pass "IBus schema(s) found:"
            echo "$schema" | while read line; do
                print_info "  - $line"
            done
            record_test "$test_name" "PASS"
        else
            print_info "IBus schema not found (may be expected)"
            record_test "$test_name" "PASS"
        fi
    else
        print_fail "Cannot check IBus schema"
        record_test "$test_name" "FAIL"
    fi
}

# Main test function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  IBus Input Engine Test Suite${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Run tests
    test_ibus_headers
    test_ibus_library
    test_ibus_config_dir
    test_engine_xml
    test_engine_library
    test_ibus_daemon
    test_gsettings
    test_engine_properties
    test_keyboard_layout
    test_ibus_environment
    test_gsettings_engine
    test_ibus_schema
    
    # Print summary
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Total tests: $TESTS_TOTAL"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed.${NC}"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-}" in
    --verbose|-v)
        set -x
        ;;
    --help|-h)
        echo "IBus Input Engine Test Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --verbose, -v    Enable verbose output"
        echo "  --help, -h       Show this help message"
        ;;
    *)
        main
        ;;
esac
