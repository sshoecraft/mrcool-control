# Installation and Deployment Guide

## Overview

This repository contains complete control and monitoring tools for the Mr Cool MDUO18060 air-source heat pump system. The tools provide bidirectional UART communication for real-time monitoring and control.

## System Requirements

### Hardware
- **Mr Cool MDUO18060** (or compatible Gree system)
- **Raspberry Pi** or similar Linux system with UART access
- **Serial connection** to HVAC WiFi module (9600 baud, 8N1)

### Software
- **Python 3.6+**
- **pyserial** library
- **requests** library (for dashboard integration)

## Quick Installation

### 1. Clone Repository
```bash
git clone https://github.com/sshoecraft/mrcool-control.git
cd mrcool-control
```

### 2. Run Setup
```bash
./setup.sh
```

### 3. Test Connection
```bash
# Check system status
python3 tools/real_time_control.py --status

# Interactive control
python3 tools/real_time_control.py --interactive
```

## Available Tools

### Core Control Tools
- **`real_time_control.py`** - Complete interactive control interface
- **`refrigerant_control_test.py`** - Advanced refrigerant circuit testing
- **`uart_control_test.py`** - Basic bidirectional control testing

### Analysis Tools
- **`comprehensive_decoder.py`** - Multi-source protocol decoder
- **`packet_analyzer.py`** - Interactive packet analysis
- **`dashboard_integration.py`** - Dashboard correlation monitoring

### Monitoring Tools
- **`enhanced_decoder.py`** - Real-time packet monitoring
- **`packet_capture.py`** - Raw packet capture utility

## Safety Considerations

### Temperature Control Testing
- Start with small temperature changes (±2°C)
- Monitor system response before larger adjustments
- Always verify changes via dashboard correlation

### Refrigerant Circuit Control
- Only use refrigerant controls if you understand HVAC systems
- Heat/Cool mode switching causes large temperature changes
- Monitor liquid/vapor temperatures during testing
- System has built-in safety protections

### Power Control
- System power control affects entire HVAC operation
- Coordinate with other building systems if applicable
- Have manual override capability available

## Troubleshooting

### UART Access Issues
```bash
# Check UART device
ls -la /dev/serial*

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again

# Test UART access
python3 -c \"import serial; ser=serial.Serial('/dev/serial0', 9600); print('OK')\"
```

### Python Dependencies
```bash
# Install missing packages
pip3 install pyserial requests

# Or use system packages
sudo apt-get install python3-serial python3-requests
```

## Contributing

This project builds on research from:
- **Bekmansurov**: Original UART protocol reverse engineering
- **evilwombat**: WiFi control implementation
- **Daikin community**: Bit-field analysis

Contributions welcome for:
- Additional system testing and validation
- Protocol extension documentation
- Integration development
- Bug fixes and improvements
