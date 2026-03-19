#!/bin/bash
# IBus Input Engine Configuration Script
# Copyright (C) 2026 Tars AI Assistant
# Licensed under LGPL v2.1+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IBus Input Engine Configuration${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if root
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

# Function to get user input
get_input() {
    read -p "$1" -e
}

# Function to configure engine properties
configure_properties() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Configuring Engine Properties${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Available properties:"
    echo "  InputMode          - Set input mode (Normal, FullWidth, HalfWidth, etc.)"
    echo "  CursorStyle        - Set cursor style (Blinking, Static)"
    echo "  ShowPreedit        - Show/hide preedit buffer"
    echo "  SoundEnabled       - Enable/disable input sound"
    echo ""
    
    # Get user choice
    echo -n "Select property to configure (enter 'all' for all): "
    read -r property
    
    case "$property" in
        InputMode)
            echo ""
            echo "Available modes:"
            echo "  Normal             - Normal input mode"
            echo "  FullWidth          - Full-width characters"
            echo "  HalfWidth          - Half-width characters"
            echo "  WideLatin          - Wide Latin characters"
            echo "  NarrowLatin        - Narrow Latin characters"
            echo ""
            echo -n "Select mode (enter 'default' for default): "
            read -r mode
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine InputMode "$mode"
            print_info "InputMode configured to: $mode"
            ;;
        CursorStyle)
            echo ""
            echo "Available styles:"
            echo "  Blinking           - Blinking cursor"
            echo "  Static             - Static cursor"
            echo ""
            echo -n "Select cursor style (enter 'default' for default): "
            read -r style
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine CursorStyle "$style"
            print_info "CursorStyle configured to: $style"
            ;;
        ShowPreedit)
            echo ""
            echo "Available options:"
            echo "  Always             - Always show preedit buffer"
            echo "  Never              - Never show preedit buffer"
            echo "  Auto               - Auto show/hide based on context"
            echo ""
            echo -n "Select preedit visibility (enter 'auto' for default): "
            read -r visibility
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine ShowPreedit "$visibility"
            print_info "ShowPreedit configured to: $visibility"
            ;;
        SoundEnabled)
            echo ""
            echo "Available options:"
            echo "  Enabled            - Enable input sound"
            echo "  Disabled           - Disable input sound"
            echo ""
            echo -n "Select sound setting (enter 'enabled' for default): "
            read -r sound
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine SoundEnabled "$sound"
            print_info "SoundEnabled configured to: $sound"
            ;;
        all)
            echo ""
            echo "Configuring all properties with default values..."
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine InputMode "Normal"
            print_info "InputMode: Normal"
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine CursorStyle "Blinking"
            print_info "CursorStyle: Blinking"
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine ShowPreedit "Auto"
            print_info "ShowPreedit: Auto"
            
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine SoundEnabled "Enabled"
            print_info "SoundEnabled: Enabled"
            ;;
        *)
            print_warning "Unknown property: $property"
            ;;
    esac
}

# Function to set default input method
set_default_input_method() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Setting Default Input Method${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Setting my-input-engine as default input method..."
    
    $SUDO gsettings set org.freedesktop.ibus.settings.inputmethod default-input-method "my-input-engine"
    
    print_info "Default input method set to: my-input-engine"
    
    # Enable the engine
    $SUDO gsettings set org.freedesktop.ibus.settings.inputmethod enabled-engines "['my-input-engine']"
    
    print_info "Engine enabled."
}

# Function to configure hotkeys
configure_hotkeys() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Configuring Hotkeys${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Default hotkeys:"
    echo "  Switch to next input method: Super+Shift (or ISO_Level3_Shift)"
    echo "  Switch to previous input method: Super+Shift+Ctrl"
    echo ""
    
    echo "Hotkeys can be customized in:"
    echo "  ~/.config/ibus/ibus.conf"
    echo "  /etc/ibus/ibus.conf"
    
    read -p "Do you want to open the configuration file? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "$HOME/.config/ibus/ibus.conf" ]; then
            $SUDO xdg-open "$HOME/.config/ibus/ibus.conf"
        else
            print_warning "Configuration file not found. Using default settings."
        fi
    fi
}

# Function to configure keyboard layout
configure_keyboard_layout() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Configuring Keyboard Layout${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Select keyboard layout:"
    echo "  1. US International"
    echo "  2. Chinese (Pinyin)"
    echo "  3. Japanese (Kana)"
    echo "  4. Korean (Hangul)"
    echo ""
    
    read -p "Enter layout number (1-4): " -i "" layout_num
    
    case "$layout_num" in
        1)
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine keyboard-layout "us"
            print_info "Keyboard layout set to: US International"
            ;;
        2)
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine keyboard-layout "zh_cn"
            print_info "Keyboard layout set to: Chinese (Pinyin)"
            ;;
        3)
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine keyboard-layout "ja"
            print_info "Keyboard layout set to: Japanese (Kana)"
            ;;
        4)
            $SUDO gsettings set org.freedesktop.ibus.engine.my-input-engine keyboard-layout "ko"
            print_info "Keyboard layout set to: Korean (Hangul)"
            ;;
        *)
            print_warning "Invalid layout number. Using default."
            ;;
    esac
}

# Function to restart IBus daemon
restart_ibus_daemon() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Restarting IBus Daemon${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Stopping IBus daemon..."
    $SUDO ibus-daemon --exit
    
    echo "Starting IBus daemon..."
    $SUDO ibus-daemon --replace
    
    echo "IBus daemon restarted successfully."
}

# Function to show configuration status
show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Current Configuration Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo ""
    echo "Current settings:"
    echo ""
    
    echo "Default input method:"
    $SUDO gsettings get org.freedesktop.ibus.settings.inputmethod default-input-method
    echo ""
    
    echo "Enabled engines:"
    $SUDO gsettings get org.freedesktop.ibus.settings.inputmethod enabled-engines
    echo ""
    
    echo "Engine properties:"
    echo "  InputMode: $(gsettings get org.freedesktop.ibus.engine.my-input-engine InputMode)"
    echo "  CursorStyle: $(gsettings get org.freedesktop.ibus.engine.my-input-engine CursorStyle)"
    echo "  ShowPreedit: $(gsettings get org.freedesktop.ibus.engine.my-input-engine ShowPreedit)"
    echo "  SoundEnabled: $(gsettings get org.freedesktop.ibus.engine.my-input-engine SoundEnabled)"
    echo ""
}

# Main configuration function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Configuration Wizard${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Parse command line arguments
    case "${1:-}" in
        --properties)
            configure_properties
            ;;
        --default)
            set_default_input_method
            restart_ibus_daemon
            ;;
        --hotkeys)
            configure_hotkeys
            ;;
        --layout)
            configure_keyboard_layout
            ;;
        --status)
            show_status
            ;;
        --restart)
            restart_ibus_daemon
            ;;
        --help|-h)
            show_help
            ;;
        *)
            # Full configuration
            echo ""
            echo "Available options:"
            echo "  --properties     Configure engine properties"
            echo "  --default        Set as default input method"
            echo "  --hotkeys        Configure hotkeys"
            echo "  --layout         Configure keyboard layout"
            echo "  --status         Show current configuration status"
            echo "  --restart        Restart IBus daemon"
            echo "  --help           Show this help message"
            echo ""
            echo "Select an option: "
            
            read -p "Enter option (or press Enter for --default): " option
            
            case "$option" in
                --properties)
                    configure_properties
                    ;;
                --default)
                    set_default_input_method
                    restart_ibus_daemon
                    ;;
                --hotkeys)
                    configure_hotkeys
                    ;;
                --layout)
                    configure_keyboard_layout
                    ;;
                --status)
                    show_status
                    ;;
                --restart)
                    restart_ibus_daemon
                    ;;
                "")
                    set_default_input_method
                    restart_ibus_daemon
                    ;;
                *)
                    print_warning "Unknown option: $option"
                    ;;
            esac
            
            echo ""
            show_status
            ;;
    esac
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  Configuration completed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    print_info "You may need to log out and log back in for changes to take effect."
}

# Show help
show_help() {
    echo "IBus Input Engine Configuration Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --properties     Configure engine properties"
    echo "  --default        Set as default input method"
    echo "  --hotkeys        Configure hotkeys"
    echo "  --layout         Configure keyboard layout"
    echo "  --status         Show current configuration status"
    echo "  --restart        Restart IBus daemon"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --default          Set as default input method"
    echo "  $0 --properties       Configure engine properties"
    echo "  $0 --layout 1         Set keyboard layout (1=US International)"
    echo "  $0 --status           Show current configuration"
}

# Run main function
main "$@"
