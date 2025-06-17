# Mr Cool Control - Complete HVAC Control System

*Formerly: GREE HVAC Protocol - Updated with Bidirectional Control Discovery*

## Major Update: Bidirectional UART Control Confirmed

**BREAKING**: The Mr Cool MDUO18060 system supports **full bidirectional control** via UART, not just monitoring.

### Updated Protocol Understanding

Your system actually implements **dual packet formats** on the same UART connection:

| Direction | Format | Size | Purpose | Example |
|-----------|--------|------|---------|---------| 
| **Query** → AC | `7e7e 02 02 [cs]` | 5 bytes | Request status | `7e7e020204` |
| **Status** ← AC | `7e7e ff e0 [data]` | 255 bytes | Status response | `7e7effe0013c30...` |
| **Control** → AC | `7e7e 25 01 [data]` | 40 bytes | Control command | `7e7e2501010000...` |

## Key Control Scripts

### 🧠 Core Scripts - Ready to Deploy

- **`smart_max_performance.py`** - **★ PRIMARY CONTROL SCRIPT ★**
  - Intelligently detects heat/cool mode via refrigerant temperature differential
  - Sets aggressive setpoints: 18°C cooling / 30°C heating
  - Maximizes compressor capacity, flow, and fan speed automatically
  - **Currently running on production system**

- **`enhanced_gree_controller.py`** - Complete interactive control interface
  - Full bidirectional control with safety checks
  - Interactive menu system for manual operation
  - Real-time status monitoring and display

- **`enhanced_gree_collector.py`** - Advanced data collection and monitoring
  - Comprehensive protocol analysis using all research findings
  - CSV logging with temperature correlations
  - Real-time performance tracking

- **`chiller_mode_controller.py`** - Maximum capacity chiller operation
  - Forces sustained maximum performance with safety monitoring
  - Continuous operation with automatic safety cutoffs
  - Dashboard integration for enhanced monitoring

## Research Integration

This documentation now incorporates findings from:

### 1. ✅ Bekmansurov Research (Original Foundation)
- **Repository**: bekmansurov/gree-hvac-protocol
- **Contribution**: UART protocol structure, temperature encoding (°C - 16)
- **Issue #6**: Swing mode encoding and packet structure updates
- **Validation**: ✅ Confirmed on Mr Cool system

### 2. ✅ evilwombat WiFi Protocol (Control Methods)
- **Repository**: evilwombat/GreeControl
- **Contribution**: Complete control implementation, 40-byte control packets
- **Features**: Temperature, mode, fan, timer, swing control
- **Adaptation**: ✅ WiFi control format works on UART

### 3. ✅ Daikin Analysis (Bit-Field Mapping)
- **Source**: GitHub issue #3 (Daikin FTKS18VL216A)
- **Contribution**: Detailed bit-field structure documentation
- **Fields**: Power, mode, fan_speed, set_temp, turbo, xfan, display_light
- **Validation**: ✅ Perfect correlation with Mr Cool system

## Quick Start

### Installation
```bash
git clone https://github.com/sshoecraft/mrcool-control.git
cd mrcool-control
./setup.sh
```

### Basic Usage
```bash
# Run smart max performance (production script)
python3 smart_max_performance.py

# Interactive control interface
python3 enhanced_gree_controller.py

# Start data collection
python3 enhanced_gree_collector.py --duration 60

# Check system status only
python3 enhanced_gree_controller.py --status
```

## Available Tools

### 🎯 Production Control Scripts
- **`smart_max_performance.py`** - Smart mode detection and optimization
- **`enhanced_gree_controller.py`** - Complete interactive control
- **`enhanced_gree_collector.py`** - Advanced monitoring and logging
- **`chiller_mode_controller.py`** - Maximum capacity operation

### 🔧 Development & Testing Tools
- **`tools/comprehensive_decoder.py`** - Multi-source protocol decoder
- **`tools/packet_analyzer.py`** - Interactive packet analysis
- **`tools/refrigerant_control_test.py`** - Advanced refrigerant circuit testing
- **`tools/uart_control_test.py`** - Basic bidirectional control testing
- **`tools/smart_max_performance.py`** - Maximum performance optimization

## Features

### ✅ Complete HVAC Control
- **Power control** - System on/off
- **Operating modes** - Auto/Cool/Heat/Fan/Dry  
- **Temperature control** - Setpoint adjustment
- **Fan speed control** - 0-5 speed levels
- **Advanced features** - Turbo, X-Fan, display control

### ✅ Advanced Refrigerant Circuit Control
- **Compressor capacity modulation** - Variable speed control
- **Refrigerant flow control** - Electronic expansion valve
- **Heat/Cool mode switching** - Reversing valve operation
- **Real-time monitoring** - Operational status feedback

### ✅ Smart Mode Detection
- **Automatic heat/cool detection** - via refrigerant temperature differential
- **Intelligent setpoint optimization** - aggressive but safe temperature targets
- **Maximum performance activation** - compressor, flow, and fan optimization
- **Production-ready automation** - suitable for continuous operation

## Hardware Compatibility

### Supported Systems
- **Mr Cool MDUO18060** (primary tested system)
- **Gree FLEXX60HP230V1AO** (rebadged version)
- **Other Gree systems** with compatible UART protocol

### Connection Requirements
- **Serial Port**: `/dev/serial0` or similar UART interface
- **Settings**: 9600 baud, 8N1
- **Access**: Read/write permissions required

## Safety Features

- **Parameter validation** - Range checking for all controls
- **Confirmation prompts** - For potentially disruptive operations
- **Error handling** - Comprehensive exception management
- **System monitoring** - Continuous status verification
- **Temperature differential analysis** - Smart mode detection prevents conflicts

## Documentation

- **[INSTALL.md](INSTALL.md)** - Complete installation and deployment guide
- **[REFRIGERANT_CONTROL_DISCOVERY.md](REFRIGERANT_CONTROL_DISCOVERY.md)** - Advanced control documentation
- **[packet-analysis.md](packet-analysis.md)** - Protocol structure details
- **[RESEARCH_TASKS.md](RESEARCH_TASKS.md)** - Future development roadmap

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

## References

- [Bekmansurov GREE HVAC Protocol](https://github.com/bekmansurov/gree-hvac-protocol)
- [evilwombat GreeControl](https://github.com/evilwombat/GreeControl)
- [Daikin Protocol Analysis](https://github.com/bekmansurov/gree-hvac-protocol/issues/3)

---

**Status**: Complete bidirectional control system ready for production use with smart optimization scripts.
