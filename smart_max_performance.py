#!/usr/bin/env python3
"""
SMART MAXIMUM PERFORMANCE SCRIPT
Detects heat/cool mode and sets appropriate aggressive setpoint
+ maximum capacity/flow/fan for both modes
"""

import serial
import time
from datetime import datetime

def calc_checksum(buf):
    return sum(buf[2:-1]) & 0xff

def create_control_packet(power=None, capacity=None, flow=None, fan=None, temp=None):
    packet = bytearray(40)
    packet[0:4] = [0x7e, 0x7e, 37, 0x01]  # Header
    packet[4] = 0x01  # Update flag
    
    if power is not None:
        packet[5] = 0x80 if power else 0x00
    if capacity is not None:
        packet[6] = capacity & 0xFF
    if flow is not None:
        packet[7] = flow & 0xFF
    if temp is not None:
        temp_val = int(temp - 16)  # Bekmansurov encoding
        if 0 <= temp_val <= 15:
            packet[9] = (packet[9] & 0x0F) | ((temp_val & 0x0F) << 4)
    if fan is not None:
        packet[19] = fan & 0x07
        
    packet[39] = calc_checksum(packet)
    return packet

def get_current_mode():
    """Query system to detect current heat/cool mode"""
    try:
        ser = serial.Serial('/dev/serial0', 9600, timeout=1)
        
        # Send query
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        ser.write(query)
        time.sleep(0.3)
        
        response = ser.read(300)
        ser.close()
        
        if response and len(response) > 31:
            # Analyze operational byte and temperature patterns
            op_byte = response[31] if len(response) > 31 else 0
            liquid_temp = response[64] if len(response) > 64 else 0
            vapor_temp = response[25] if len(response) > 25 else 0
            
            # Detect mode based on temperature differential pattern
            temp_diff = liquid_temp - vapor_temp
            
            print(f"📊 Current readings: Liquid={liquid_temp}°C, Vapor={vapor_temp}°C, Diff={temp_diff}°C")
            
            # Heat mode: liquid should be cooler than vapor (heat pump reversed)
            # Cool mode: liquid should be warmer than vapor (normal AC)
            if temp_diff < 0:
                return 'HEAT', liquid_temp, vapor_temp
            elif temp_diff > 20:
                return 'COOL', liquid_temp, vapor_temp
            else:
                return 'UNKNOWN', liquid_temp, vapor_temp
                
    except Exception as e:
        print(f"Error detecting mode: {e}")
        return 'UNKNOWN', 0, 0

def smart_max_performance():
    print("🧠 SMART MAXIMUM PERFORMANCE SCRIPT 🧠")
    print(f"Time: {datetime.now()}")
    print("Detecting current mode and optimizing accordingly...")
    
    # Detect current mode
    mode, liquid_temp, vapor_temp = get_current_mode()
    print(f"\n🔍 Detected mode: {mode}")
    
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    
    try:
        if mode == 'COOL':
            print("\n❄️  COOLING MODE - Maximum Cooling Configuration")
            target_temp = 18  # Aggressive cooling: 18°C (64.4°F)
            emoji = "❄️"
            action = "MAXIMUM COOLING"
            
        elif mode == 'HEAT':
            print("\n🔥 HEATING MODE - Maximum Heating Configuration") 
            target_temp = 30  # Aggressive heating: 30°C (86°F)
            emoji = "🔥"
            action = "MAXIMUM HEATING"
            
        else:
            print("\n🤔 UNKNOWN MODE - Using moderate settings")
            target_temp = 24  # Moderate: 24°C (75°F) 
            emoji = "⚡"
            action = "MAXIMUM PERFORMANCE"
        
        print(f"\n{emoji} {action} ACTIVATION {emoji}")
        
        # Step 1: Power ON
        print("⚡ Power ON...")
        power_packet = create_control_packet(power=True)
        ser.write(power_packet)
        time.sleep(1)
        
        # Step 2: Set aggressive setpoint based on mode
        print(f"🌡️  Setting aggressive {target_temp}°C ({target_temp * 9/5 + 32:.1f}°F) setpoint...")
        temp_packet = create_control_packet(
            power=True,
            temp=target_temp
        )
        ser.write(temp_packet)
        time.sleep(1)
        
        # Step 3: Maximum Compressor Capacity
        print("🔧 Compressor capacity to MAXIMUM (0x80)...")
        capacity_packet = create_control_packet(
            power=True,
            capacity=0x80
        )
        ser.write(capacity_packet)
        time.sleep(1)
        
        # Step 4: Maximum Refrigerant Flow
        print("🌊 Refrigerant flow to MAXIMUM (0x80)...")
        flow_packet = create_control_packet(
            power=True,
            flow=0x80
        )
        ser.write(flow_packet)
        time.sleep(1)
        
        # Step 5: Maximum Fan Speed
        print("💨 Fan speed to MAXIMUM (5)...")
        fan_packet = create_control_packet(
            power=True,
            fan=5
        )
        ser.write(fan_packet)
        time.sleep(1)
        
        print(f"\n✅ AC OPTIMIZED FOR {action}! ✅")
        print("Configuration:")
        print(f"  🔥 Power: ON")
        print(f"  🌡️  Setpoint: {target_temp}°C ({target_temp * 9/5 + 32:.1f}°F) - AGGRESSIVE {mode}!")
        print(f"  🔧 Compressor: MAXIMUM capacity (0x80)")
        print(f"  🌊 Refrigerant: MAXIMUM flow (0x80)")
        print(f"  💨 Fan: MAXIMUM (speed 5)")
        print(f"  🏠 Mode: Detected as {mode} (thermostat controlled)")
        print(f"\n🎉 SYSTEM JUICED FOR {action}! 🎉")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()

if __name__ == '__main__':
    smart_max_performance()
