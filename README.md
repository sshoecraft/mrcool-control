# HVAC Control System - Mr Cool MDUO18060

## Current Status: UART Control Limitation Discovered

After extensive reverse engineering and protocol analysis, we have determined that **direct UART control via the COMM port is not feasible** for full system control of the Mr Cool MDUO18060 heat pump.

### What Works via UART
- ✅ **Complete monitoring and telemetry** via `hvac_monitor.py`
- ✅ **Real-time pressure readings** (vapor/liquid lines)
- ✅ **Temperature monitoring** (refrigerant lines, heat exchangers)
- ✅ **System status and performance metrics**
- ✅ **Flow control analysis and optimization detection**

### What Doesn't Work via UART
- ❌ **Direct system control commands** (power, mode, setpoint changes)
- ❌ **Compressor speed control**
- ❌ **Refrigerant flow valve control**
- ❌ **Performance mode switching**

## New Control Strategy: Modbus Gateway Integration

### Phase 1: Gree Modbus Gateway (Planned)
We will acquire and integrate a **Gree Modbus Gateway** to connect to the **CN6 port** on the indoor unit for proper bidirectional control.

**Hardware Requirements:**
- Gree Modbus Gateway module
- RS485 to USB/Ethernet adapter
- Connection to CN6 port on indoor unit

**Expected Capabilities:**
- Full system control (power, modes, setpoints)
- Advanced performance parameter adjustment
- Integration with existing monitoring system

### Phase 2: Physical Override System (Interim Solution)

While waiting for Modbus hardware, we will implement physical sensor manipulation:

#### Vapor Line Heat Tape
- **Purpose**: Artificially raise vapor line temperature
- **Method**: Controlled heat tape wrapped around vapor line sensor
- **Goal**: Trick system into higher performance mode by simulating low refrigerant flow

#### Ambient Temperature Control
- **Target**: Maintain 72°F at ambient temperature sensor
- **Method**: Peltier cooling module with precise temperature control
- **Purpose**: Override outdoor temperature readings to force optimal operating conditions

## Current Monitoring Capability

### hvac_monitor.py
The only maintained script in this repository. Provides comprehensive real-time monitoring via network connection to the HVAC unit:

**Features:**
- Real-time pressure readings (vapor/liquid refrigerant lines)
- Temperature monitoring across all sensors
- System status and performance metrics
- Automatic mode detection (Heat/Cool/Off)
- Compact continuous display with color-coded indicators

**Usage:**
```bash
# Default connection (192.168.1.188)
python3 hvac_monitor.py

# Custom hostname/IP
python3 hvac_monitor.py 192.168.1.100
python3 hvac_monitor.py ac1.localdomain
```

Connects to HVAC unit on port 23 and displays live telemetry data.

## Hardware Setup

### Current Configuration
- **Serial**: `/dev/serial0` (9600 baud, 8N1)
- **Network Monitoring**: Port 23 on AC1 unit (192.168.1.188)
- **Protocol**: Custom GREE UART (7E 7E header, 40-byte control, 255-byte status)

### Planned Modbus Configuration
- **Interface**: CN6 port on indoor unit
- **Protocol**: Modbus RTU over RS485
- **Gateway**: Gree Modbus Gateway module
- **Integration**: Python modbus-tk library

## Pressure and Temperature Monitoring

The system provides accurate real-time monitoring:

### Pressure Sensors
- **Vapor Line**: Position 16 (bar×10 encoding) - Typical: ~112 PSI
- **Liquid Line**: Positions 60-61 (kPa little-endian) - Typical: ~260-285 PSI

### Temperature Sensors
- **Vapor Line**: Position 22 (°F direct)
- **Liquid Line**: Position 56 (scaled)
- **Outdoor Coil**: Position 25 (°C, Bekmansurov encoding)
- **Indoor Heat Exchanger**: Position 64 (°C)

## Development Timeline

1. **Immediate** - Physical sensor override implementation
2. **Short-term** - Gree Modbus Gateway procurement and integration
3. **Medium-term** - Complete control system integration
4. **Long-term** - Automated optimization with both monitoring and control

## Safety and Compliance

All modifications maintain system safety limits:
- Maximum liquid temperature: 65°C
- Minimum vapor temperature: -10°C
- Maximum temperature differential: 60°C
- Pressure monitoring with automatic safety shutdowns

---

*This project represents comprehensive reverse engineering of the GREE HVAC protocol with full monitoring capabilities and planned expansion to complete control via Modbus integration.*