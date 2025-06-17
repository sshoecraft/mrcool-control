#!/usr/bin/env python3
"""
Refrigerant Circuit Control Test
Advanced HVAC control capabilities for Mr Cool MDUO18060
Based on refrigerant control discovery from June 16, 2025
"""

import serial
import time
from datetime import datetime

class RefrigerantController:
    def __init__(self, port='/dev/serial0', baud=9600):
        self.port = port
        self.baud = baud
        self.ser = None
        
    def connect(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        print(f"Connected to {self.port}")
        
    def disconnect(self):
        if self.ser:
            self.ser.close()
            
    def calc_checksum(self, buf):
        """Calculate checksum for packet"""
        return sum(buf[2:-1]) & 0xff
        
    def send_query(self):
        """Send status query command"""
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        
        print(f"Sending query: {query.hex()}")
        self.ser.write(query)
        
        time.sleep(0.3)
        response = self.ser.read(300)
        
        if response and response.startswith(b'\\x7e\\x7e'):
            return response
        return None
        
    def create_refrigerant_control_packet(self, power=None, capacity=None, flow=None, mode=None):
        """
        Create refrigerant circuit control packet
        
        Args:
            power: 0x80 = ON, 0x00 = OFF
            capacity: 0x20-0x80 (compressor capacity modulation)
            flow: 0x10-0x80 (refrigerant flow / expansion valve)
            mode: 0x10 = Heat, 0x20 = Cool (reversing valve)
        """
        packet = bytearray(40)
        packet[0:4] = [0x7e, 0x7e, 37, 0x01]  # Header
        
        # Update flag
        packet[4] = 0x01
        
        # Control positions discovered June 16, 2025
        if power is not None:
            packet[5] = power          # Position 5: Power Control
        if capacity is not None:
            packet[6] = capacity       # Position 6: Compressor Capacity
        if flow is not None:
            packet[7] = flow          # Position 7: Refrigerant Flow
        if mode is not None:
            packet[8] = mode          # Position 8: Heat/Cool Mode
            
        # Calculate checksum
        packet[39] = self.calc_checksum(packet)
        return packet
        
    def comprehensive_test(self):
        """Run all refrigerant control tests"""
        print("=== REFRIGERANT CIRCUIT CONTROL TEST ===")
        print(f"Time: {datetime.now()}")
        print("Mr Cool MDUO18060 / Gree FLEXX60HP230V1AO")
        print("Based on discovery from June 16, 2025")
        
        try:
            self.test_power_control()
            self.test_compressor_capacity()
            self.test_refrigerant_flow()
            
            # Ask before mode test (causes large temperature changes)
            response = input("\\nRun heat/cool mode test? This causes large temperature changes (y/N): ")
            if response.lower() == 'y':
                self.test_heat_cool_mode()
            else:
                print("Skipping heat/cool mode test")
                
        except KeyboardInterrupt:
            print("\\nTest interrupted by user")
        except Exception as e:
            print(f"Test error: {e}")

def main():
    controller = RefrigerantController()
    
    try:
        controller.connect()
        controller.comprehensive_test()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()

if __name__ == '__main__':
    main()
