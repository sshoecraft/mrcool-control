#!/usr/bin/env python3
"""
Mr Cool MDUO18060 Chiller Mode Controller
Forces maximum capacity operation while monitoring safety parameters
"""

import serial
import time
from datetime import datetime

class ChillerModeController:
    def __init__(self, port='/dev/serial0', baud=9600):
        self.port = port
        self.baud = baud
        self.ser = None
        self.safety_limits = {
            'max_liquid_temp_c': 65,    # 149°F max liquid temp
            'min_vapor_temp_c': -10,    # -14°F min vapor temp  
            'max_temp_diff_c': 60,      # Max liquid-vapor differential
            'min_operational': 10,      # Min operational value
            'max_operational': 255      # Max operational value
        }
        
    def connect(self):
        """Connect to heat pump UART"""
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        print(f"Connected to {self.port}")
        
    def disconnect(self):
        """Disconnect from UART"""
        if self.ser:
            self.ser.close()
            
    def get_system_status(self):
        """Get current system status and safety parameters"""
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        self.ser.write(query)
        time.sleep(0.3)
        
        response = self.ser.read(500)
        for i in range(len(response) - 10):
            if response[i:i+2] == b'\x7e\x7e' and len(response) > i+2 and response[i+2] == 0xff:
                packet = response[i:i+255]
                if len(packet) > 64:
                    return {
                        'power_on': packet[10] == 0xAA,
                        'vapor_temp_c': packet[25],
                        'operational': packet[31],
                        'liquid_temp_c': packet[64],
                        'temp_diff_c': packet[64] - packet[25],
                        'timestamp': datetime.now()
                    }
        return None
        
    def check_safety_limits(self, status):
        """Check if system is operating within safe limits"""
        if not status:
            return False, "No status data"
            
        safety_issues = []
        
        if status['liquid_temp_c'] > self.safety_limits['max_liquid_temp_c']:
            safety_issues.append(f"Liquid temp too high: {status['liquid_temp_c']}°C")
            
        if status['vapor_temp_c'] < self.safety_limits['min_vapor_temp_c']:
            safety_issues.append(f"Vapor temp too low: {status['vapor_temp_c']}°C")
            
        if status['temp_diff_c'] > self.safety_limits['max_temp_diff_c']:
            safety_issues.append(f"Temperature differential too high: {status['temp_diff_c']}°C")
            
        if not (self.safety_limits['min_operational'] <= status['operational'] <= self.safety_limits['max_operational']):
            safety_issues.append(f"Operational value out of range: {status['operational']}")
            
        return len(safety_issues) == 0, safety_issues
        
    def send_max_capacity_command(self, mode='cool', include_fan=True):
        """Send maximum capacity command for chiller operation"""
        packet = bytearray(40)
        packet[0:4] = [0x7e, 0x7e, 37, 0x01]  # Header
        
        # Force maximum capacity settings
        packet[4] = 0x01    # Update flag
        packet[5] = 0x80    # Power ON
        packet[6] = 0xFF    # MAXIMUM compressor capacity
        packet[7] = 0xFF    # MAXIMUM refrigerant flow
        
        # Set cooling mode for chiller operation
        if mode == 'cool':
            packet[8] = 0x20  # Cool mode
        elif mode == 'heat':
            packet[8] = 0x10  # Heat mode (for reverse cycle chiller)
        else:
            packet[8] = 0x00  # Auto mode
            
        # Add maximum fan speed control in multiple positions
        if include_fan:
            packet[5] |= 0x03   # Add fan bits to power byte
            packet[8] |= 0x03   # Add fan bits to mode byte
            packet[9] = 0xFF    # Fan position 9
            packet[19] = 0xFF   # Fan position 19 (evilwombat)
            packet[22] = 0xFF   # Fan position 22
            
        # Calculate checksum
        checksum = sum(packet[2:-1]) & 0xFF
        packet[-1] = checksum
        
        print(f"Sending max capacity command (mode={mode}, fan={include_fan}): {packet.hex()}")
        self.ser.write(packet)
        return packet
        
    def monitor_and_maintain_max_capacity(self, duration_minutes=60, check_interval=30):
        """Continuously monitor and maintain maximum capacity operation"""
        print(f"Starting chiller mode - Maximum capacity for {duration_minutes} minutes")
        print(f"Safety monitoring every {check_interval} seconds")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        last_command_time = 0
        command_interval = 300  # Re-send max capacity command every 5 minutes
        
        # Initial max capacity command
        self.send_max_capacity_command('cool')
        last_command_time = time.time()
        
        while time.time() < end_time:
            # Get current status
            status = self.get_system_status()
            
            if status:
                # Check safety limits
                is_safe, issues = self.check_safety_limits(status)
                
                # Display status
                elapsed = time.time() - start_time
                remaining = (end_time - time.time()) / 60
                
                print(f"\nTime: {status['timestamp'].strftime('%H:%M:%S')} | "
                      f"Elapsed: {elapsed/60:.1f}min | Remaining: {remaining:.1f}min")
                print(f"Status: Power={'ON' if status['power_on'] else 'OFF'} | "
                      f"Op={status['operational']} | "
                      f"Temps: {status['vapor_temp_c']}°C/{status['liquid_temp_c']}°C | "
                      f"Diff: {status['temp_diff_c']}°C")
                
                if not is_safe:
                    print("⚠️  SAFETY ALERT:")
                    for issue in issues:
                        print(f"   - {issue}")
                    
                    # If liquid temp too high, reduce capacity temporarily
                    if status['liquid_temp_c'] > self.safety_limits['max_liquid_temp_c']:
                        print("🛡️  Reducing capacity for safety...")
                        packet = bytearray(40)
                        packet[0:4] = [0x7e, 0x7e, 37, 0x01]
                        packet[4] = 0x01
                        packet[5] = 0x80
                        packet[6] = 0x40  # Reduced capacity
                        packet[7] = 0x60  # Reduced flow
                        packet[8] = 0x20  # Cool mode
                        checksum = sum(packet[2:-1]) & 0xFF
                        packet[-1] = checksum
                        self.ser.write(packet)
                        time.sleep(30)  # Wait for system to stabilize
                        continue
                        
                else:
                    print("✅ System operating safely")
                    
                # Re-send max capacity command periodically to prevent scaling down
                if time.time() - last_command_time > command_interval:
                    print("🔄 Re-asserting maximum capacity...")
                    self.send_max_capacity_command('cool')
                    last_command_time = time.time()
                    
            else:
                print("❌ No system response")
                
            time.sleep(check_interval)
            
        print(f"\n🏁 Chiller mode completed. Total runtime: {duration_minutes} minutes")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mr Cool Chiller Mode Controller")
    parser.add_argument("--duration", type=int, default=60, help="Runtime in minutes")
    parser.add_argument("--mode", choices=['monitor', 'chiller'], default='chiller', 
                       help="Operation mode")
    parser.add_argument("--check-interval", type=int, default=30, help="Safety check interval (seconds)")
    
    args = parser.parse_args()
    
    controller = ChillerModeController()
    
    try:
        controller.connect()
        
        if args.mode == 'monitor':
            # Just monitor current status
            status = controller.get_system_status()
            if status:
                is_safe, issues = controller.check_safety_limits(status)
                print("Current Status:")
                print(f"  Power: {'ON' if status['power_on'] else 'OFF'}")
                print(f"  Vapor: {status['vapor_temp_c']}°C")
                print(f"  Liquid: {status['liquid_temp_c']}°C")
                print(f"  Operational: {status['operational']}")
                print(f"  Safety: {'✅ OK' if is_safe else '⚠️  Issues detected'}")
                if not is_safe:
                    for issue in issues:
                        print(f"    - {issue}")
                        
        elif args.mode == 'chiller':
            # Run chiller mode with max capacity
            controller.monitor_and_maintain_max_capacity(args.duration, args.check_interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Chiller mode stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        controller.disconnect()

if __name__ == '__main__':
    main()
