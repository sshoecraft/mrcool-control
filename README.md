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
# Check system status
python3 tools/real_time_control.py --status

# Interactive control
python3 tools/real_time_control.py --interactive

# Advanced refrigerant control testing
python3 tools/refrigerant_control_test.py
```

## Available Tools

### Control Tools
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

### ✅ Dashboard Integration
- **Temperature correlation** - UART ↔ Dashboard validation
- **Real-time monitoring** - Live system status
- **Control verification** - Command response tracking

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

**Status**: Complete bidirectional control system ready for production use.
