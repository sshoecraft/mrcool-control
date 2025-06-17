#!/bin/bash
# Setup script for Mr Cool Control repository
# Installs dependencies and prepares environment

set -e

echo \"=== Mr Cool Control Setup ===\"
echo \"Setting up development environment...\"

# Check Python version
echo \"Checking Python version...\"
python3 --version

# Install required Python packages
echo \"Installing Python dependencies...\"
pip3 install --user pyserial requests

# Make scripts executable
echo \"Making scripts executable...\"
find tools/ examples/ -name \"*.py\" -exec chmod +x {} \\;

# Check if running on ac1.localdomain (the monitoring Pi)
if [[ $(hostname) == \"ac1.localdomain\" ]]; then
    echo \"Detected ac1.localdomain - checking UART access...\"
    
    # Check UART access
    if [ -c \"/dev/serial0\" ]; then
        echo \"✓ UART port /dev/serial0 available\"
        
        # Test UART permissions
        if [ -r \"/dev/serial0\" ] && [ -w \"/dev/serial0\" ]; then
            echo \"✓ UART read/write permissions OK\"
        else
            echo \"⚠ UART permissions may need adjustment\"
            echo \"  Run: sudo usermod -a -G dialout $USER\"
            echo \"  Then logout and login again\"
        fi
    else
        echo \"✗ UART port /dev/serial0 not found\"
        echo \"  Enable UART in raspi-config if on Raspberry Pi\"
    fi
    
    # Check dashboard connectivity
    echo \"Testing dashboard connectivity...\"
    if curl -s --connect-timeout 5 http://localhost:5000/api/data > /dev/null; then
        echo \"✓ Dashboard API accessible at localhost:5000\"
    elif curl -s --connect-timeout 5 http://ac.localdomain:5000/api/data > /dev/null; then
        echo \"✓ Dashboard API accessible at ac.localdomain:5000\"
    else
        echo \"⚠ Dashboard API not responding\"
        echo \"  Start dashboard service if needed\"
    fi
    
else
    echo \"Running on $(hostname) - remote access mode\"
    echo \"Scripts will need SSH access to ac1.localdomain for UART communication\"
fi

# Test basic imports
echo \"Testing Python imports...\"
python3 -c \"import serial; print('✓ pyserial imported')\"
python3 -c \"import requests; print('✓ requests imported')\"

echo \"\"
echo \"=== Setup Complete ===\"
echo \"\"
echo \"Available tools:\"
echo \"  tools/refrigerant_control_test.py  - Advanced refrigerant circuit control\"
echo \"  tools/comprehensive_decoder.py     - Multi-source protocol decoder\"
echo \"  tools/uart_control_test.py         - Bidirectional control testing\"
echo \"  tools/packet_analyzer.py           - Interactive packet analysis\"
echo \"\"
echo \"Quick start:\"
echo \"  # Interactive control (on ac1.localdomain)\"
echo \"  python3 tools/real_time_control.py --interactive\"
echo \"\"
echo \"  # Test refrigerant controls (advanced)\"
echo \"  python3 tools/refrigerant_control_test.py\"
echo \"\"
echo \"Remote usage (from other systems):\"
echo \"  ssh root@ac1.localdomain 'cd /path/to/mrcool-control && python3 tools/real_time_control.py --status'\"
