#!/usr/bin/env python3
"""
GREE HVAC Real-Time Control Monitor
Displays decoded control values from AC unit packets
"""

import socket
import time
from datetime import datetime
import sys

class GreeHVACMonitor:
    def __init__(self, host, port=23):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def decode_packet(self, packet):
        """Decode GREE packet into meaningful control values"""
        if len(packet) < 69:
            return None
            
        decoded = {
            # System Status
            'status_12': packet[12],
            'status_13': packet[13], 
            'status_14': packet[14],
            'status_15': packet[15],
            
            # Fan & Compressor Control
            'fan_speed': packet[16],
            'fan_enable': packet[17],
            'compressor_speed': packet[18],
            'compressor_status': packet[19],
            
            # Flow Control  
            'flow_main': packet[21],
            'flow_aux1': packet[22],
            'flow_aux2': packet[23],
            
            # Temperature Sensors (raw positions)
            'temp_pos25': packet[25],  # Outdoor coil temperature
            'temp_status': packet[26],
            'temp_pos64': packet[64], # Indoor coil temperature
            
            # Actual Refrigerant Line Temperatures (dashboard-matched positions)
            'vapor_temp_f': packet[22],        # Vapor line temperature in °F
            'liquid_temp_f': packet[56] * 0.43,  # Liquid line with scaling factor
            
            # Pressure Sensors
            'vapor_pressure_bar': packet[16] / 10.0,  # Vapor pressure in bar (×10 encoding)
            'vapor_pressure_psi': packet[16] * 1.45038,  # Vapor pressure in PSI
            'liquid_pressure_kpa': (packet[61] << 8) | packet[60],  # Liquid pressure in kPa (little-endian)
            'liquid_pressure_psi': ((packet[61] << 8) | packet[60]) * 0.145038,  # Liquid pressure in PSI
            
            # Performance Levels
            'perf_level1': packet[28],
            'perf_level2': packet[29],
            'perf_enable': packet[30],
            'perf_aux': packet[31],
            
            # System Counters
            'counter1': packet[32],
            'counter2': packet[33],
            
            # System Control
            'comp_enable': packet[38],
            'system_enable': packet[39],
            'system_mode': packet[40],
            'system_level': packet[41],
            
            # Status Registers
            'status_reg1': packet[52],
            'status_reg2': packet[59],
            
            # Checksums
            'checksum1': packet[65],
            'checksum2': packet[66],
            'checksum3': packet[67]
        }
        
        # Detect operating mode based on system_mode byte (more reliable than temperature diff)
        system_mode = decoded['system_mode']
        
        # Determine if this is a high-performance "MAX" mode based on fan/compressor speeds
        fan_speed = decoded['fan_speed']
        comp_speed = decoded['compressor_speed']
        # More aggressive MAX detection - lower thresholds and check for any high performance indicators
        is_max_mode = (fan_speed >= 60 and comp_speed >= 60) or (fan_speed >= 70) or (comp_speed >= 70) or (system_mode in [97, 98, 99, 100, 163, 226])
        
        if decoded['system_enable'] == 0:
            decoded['detected_mode'] = 'OFF'
            decoded['water_hx_temp'] = None
            decoded['outdoor_temp'] = None
        else:
            # Simply show the numeric level for all operating modes
            decoded['detected_mode'] = f'{system_mode}'
            decoded['water_hx_temp'] = decoded['temp_pos64']   # Water heat exchanger
            decoded['outdoor_temp'] = decoded['temp_pos25']    # Outdoor coil
        
        return decoded
    
    def classify_mode(self, decoded):
        """Classify operating mode based on control values"""
        fan_speed = decoded['fan_speed']
        comp_speed = decoded['compressor_speed']
        system_enable = decoded['system_enable']
        
        if system_enable == 0:
            return "OFF", "🔴"
        elif fan_speed >= 75 and comp_speed >= 75:
            return "HIGH/RUN", "🟢"
        elif fan_speed >= 50 and comp_speed >= 50:
            return "MAX", "🟡"
        elif fan_speed > 0 and comp_speed > 0:
            return "LOW", "🔵"
        else:
            return "UNKNOWN", "⚪"
    
    def format_temperature(self, temp_c):
        """Format temperature in C and F"""
        temp_f = temp_c * 9/5 + 32
        return f"{temp_c:2d}°C ({temp_f:5.1f}°F)"
    
    def print_header(self):
        """Print monitoring header"""
        print("\n" + "="*120)
        print("🔍 GREE HVAC CONTROL MONITOR - Dashboard-Style Refrigerant Line Temps & Pressures")
        print("="*120)
        print(f"{'Time':<10} {'Level':<14} {'Fan':<8} {'Comp':<8} {'Flow':<12} {'Vapor/Liquid/Differential':<32} {'Pressures V/L':<20} {'Performance':<15}")
        print("-"*120)
    
    def print_detailed_status(self, decoded, mode, mode_icon):
        """Print detailed system status"""
        print(f"\n🎯 DETAILED SYSTEM STATUS - {mode} {mode_icon}")
        print("="*60)
        
        # Fan & Compressor
        print(f"🌀 FAN CONTROL:")
        print(f"   Fan Speed (16):      0x{decoded['fan_speed']:02x} ({decoded['fan_speed']:3d})")
        print(f"   Fan Enable (17):     0x{decoded['fan_enable']:02x} ({decoded['fan_enable']:3d})")
        print(f"   Compressor (18):     0x{decoded['compressor_speed']:02x} ({decoded['compressor_speed']:3d})")
        print(f"   Comp Status (19):    0x{decoded['compressor_status']:02x} ({decoded['compressor_status']:3d})")
        
        # Flow Control
        print(f"\n💨 FLOW CONTROL:")
        print(f"   Flow Main (21):      0x{decoded['flow_main']:02x} ({decoded['flow_main']:3d})")
        print(f"   Flow Aux 1 (22):     0x{decoded['flow_aux1']:02x} ({decoded['flow_aux1']:3d})")
        print(f"   Flow Aux 2 (23):     0x{decoded['flow_aux2']:02x} ({decoded['flow_aux2']:3d})")
        
        # Dashboard-Style Temperature Display
        vapor_f = int(decoded['vapor_temp_f'])
        liquid_f = int(decoded['liquid_temp_f'])
        vapor_c = int((vapor_f - 32) * 5/9)
        liquid_c = int((liquid_f - 32) * 5/9)
        lv_diff_f = liquid_f - vapor_f
        
        temp_pos25 = decoded['temp_pos25']
        temp_pos64 = decoded['temp_pos64']
        temp_pos25_f = int(temp_pos25 * 9/5 + 32)
        temp_pos64_f = int(temp_pos64 * 9/5 + 32)
        
        print(f"\n🌡️ REFRIGERANT LINE TEMPERATURES (Dashboard Style):")
        print(f"   💨 Vapor Line:        {vapor_f}°F ({vapor_c}°C)")
        print(f"   💧 Liquid Line:       {liquid_f}°F ({liquid_c}°C)")
        print(f"   📊 L-V Differential:  {lv_diff_f}°F ({int(lv_diff_f*5/9)}°C)")
        print(f"   🔍 Detected Mode:     {decoded['detected_mode']}")
        
        print(f"\n🔧 REFRIGERANT PRESSURES:")
        print(f"   💨 Vapor Pressure:    {decoded['vapor_pressure_psi']:.1f} PSI ({decoded['vapor_pressure_bar']:.1f} bar)")
        print(f"   💧 Liquid Pressure:   {decoded['liquid_pressure_psi']:.1f} PSI ({decoded['liquid_pressure_kpa']} kPa)")
        
        print(f"\n🏠 CHILLER HEAT EXCHANGERS:")
        print(f"   🌤️  Outdoor Coil:       {temp_pos25:2d}°C ({temp_pos25_f}°F)")
        print(f"   💧 Water Heat Exchanger: {temp_pos64:2d}°C ({temp_pos64_f}°F)")
        
        if decoded['water_hx_temp'] is not None:
            water_hx_f = int(decoded['water_hx_temp'] * 9/5 + 32)
            outdoor_f = int(decoded['outdoor_temp'] * 9/5 + 32)
            print(f"   🎯 Active Water HX:   {decoded['water_hx_temp']:2d}°C ({water_hx_f}°F)")
            print(f"   🎯 Active Outdoor:    {decoded['outdoor_temp']:2d}°C ({outdoor_f}°F)")
        
        # Performance
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Perf Level 1 (28):   0x{decoded['perf_level1']:02x} ({decoded['perf_level1']:3d})")
        print(f"   Perf Level 2 (29):   0x{decoded['perf_level2']:02x} ({decoded['perf_level2']:3d})")
        print(f"   Perf Enable (30):    0x{decoded['perf_enable']:02x} ({decoded['perf_enable']:3d})")
        print(f"   Perf Aux (31):       0x{decoded['perf_aux']:02x} ({decoded['perf_aux']:3d})")
        
        # System Control
        print(f"\n🎯 SYSTEM CONTROL:")
        print(f"   Comp Enable (38):    0x{decoded['comp_enable']:02x} ({decoded['comp_enable']:3d})")
        print(f"   System Enable (39):  0x{decoded['system_enable']:02x} ({decoded['system_enable']:3d})")
        print(f"   System Mode (40):    0x{decoded['system_mode']:02x} ({decoded['system_mode']:3d})")
        print(f"   System Level (41):   0x{decoded['system_level']:02x} ({decoded['system_level']:3d})")
        
        # Status
        print(f"\n📊 STATUS:")
        print(f"   Status Bytes:        0x{decoded['status_12']:02x} 0x{decoded['status_13']:02x} 0x{decoded['status_14']:02x} 0x{decoded['status_15']:02x}")
        print(f"   Counters:            {decoded['counter1']:3d} / {decoded['counter2']:3d}")
        print(f"   Status Registers:    0x{decoded['status_reg1']:02x} / 0x{decoded['status_reg2']:02x}")
        
    def monitor_continuous(self, detailed=False):
        """Continuous monitoring mode"""
        self.print_header()
        packet_count = 0
        buffer = b''
        last_detailed = time.time()
        
        try:
            while True:
                try:
                    self.socket.settimeout(1.0)
                    data = self.socket.recv(1024)
                    if not data:
                        print("❌ Connection lost")
                        break
                        
                    buffer += data
                    
                    # Extract GREE packets
                    while len(buffer) >= 69:
                        if buffer[:4] == b'\x7e\x7e\xff\xe0':
                            packet = buffer[:69]
                            buffer = buffer[69:]
                            
                            packet_data = list(packet)
                            decoded = self.decode_packet(packet_data)
                            
                            if decoded:
                                packet_count += 1
                                mode, mode_icon = self.classify_mode(decoded)
                                
                                # Compact status line with smart temperature display
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                fan_comp = f"F:{decoded['fan_speed']:2d} C:{decoded['compressor_speed']:2d}"
                                flow_str = f"{decoded['flow_main']:3d}/{decoded['flow_aux1']:2d}/{decoded['flow_aux2']:2d}"
                                
                                # Dashboard-style temperature display
                                vapor_f = int(decoded['vapor_temp_f'])
                                liquid_f = int(decoded['liquid_temp_f'])
                                lv_diff = liquid_f - vapor_f
                                
                                # Determine mode type based on system_mode value for emoji
                                system_mode = decoded['system_mode']
                                if system_mode == 32 or system_mode in [226, 97, 98, 99, 100]:  # Heat modes
                                    temp_str = f"🔥V:{vapor_f}°F L:{liquid_f}°F Δ:{lv_diff:+d}°F"
                                elif system_mode == 204:  # Cool mode
                                    temp_str = f"❄️V:{vapor_f}°F L:{liquid_f}°F Δ:{lv_diff:+d}°F"
                                else:
                                    temp_str = f"V:{vapor_f}°F L:{liquid_f}°F Δ:{lv_diff:+d}°F"
                                    
                                mode_display = f"{decoded['detected_mode']}"
                                perf_str = f"{decoded['perf_level1']:3d}/{decoded['perf_level2']:3d}"
                                
                                # Add pressure display
                                vapor_psi = decoded['vapor_pressure_psi']
                                liquid_psi = decoded['liquid_pressure_psi']
                                pressure_str = f"{vapor_psi:3.0f}/{liquid_psi:3.0f} PSI"
                                
                                print(f"{timestamp} {mode_icon} {mode_display:<12} {fan_comp:<7} {flow_str:<11} {temp_str:<30} {pressure_str:<19} {perf_str:<14}")
                                
                                # Detailed status every 10 seconds or on mode change
                                if detailed and (time.time() - last_detailed > 10):
                                    self.print_detailed_status(decoded, mode, mode_icon)
                                    self.print_header()
                                    last_detailed = time.time()
                        else:
                            buffer = buffer[1:]
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped. Captured {packet_count} packets.")
    
    def monitor_single(self):
        """Single packet capture and detailed decode"""
        buffer = b''
        
        try:
            while True:
                self.socket.settimeout(5.0)
                data = self.socket.recv(1024)
                if not data:
                    break
                    
                buffer += data
                
                if len(buffer) >= 69 and buffer[:4] == b'\x7e\x7e\xff\xe0':
                    packet = buffer[:69]
                    packet_data = list(packet)
                    decoded = self.decode_packet(packet_data)
                    
                    if decoded:
                        mode, mode_icon = self.classify_mode(decoded)
                        self.print_detailed_status(decoded, mode, mode_icon)
                        break
                        
        except Exception as e:
            print(f"Error: {e}")
    
    def close(self):
        if self.socket:
            self.socket.close()

def main():
    # Check for command line arguments
    if len(sys.argv) != 2:
        print("Usage: hvac_monitor.py <hostname/ip>")
        print("Example: hvac_monitor.py 10.0.0.100")
        sys.exit(1)
    
    # Get hostname from command line
    host = sys.argv[1]
    
    try:
        monitor = GreeHVACMonitor(host=host)
        
        if not monitor.connect():
            return
        
        try:
            print("\n🔄 Starting continuous monitoring (Ctrl+C to stop)")
            monitor.monitor_continuous(detailed=False)
                
        finally:
            monitor.close()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
