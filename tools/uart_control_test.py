#!/usr/bin/env python3
"""
UART Control Test
Basic bidirectional control testing for Mr Cool MDUO18060
"""

import serial
import time
from datetime import datetime

class UARTController:
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
            print(f"Response length: {len(response)} bytes")
            print(f"Header: {response[:5].hex()}")
            return response
        return None
        
    def create_control_packet(self, power=None, temp=None, fan=None):
        """Create a basic control packet for testing"""
        packet = bytearray(40)
        packet[0] = 0x7e  # Sync
        packet[1] = 0x7e  # Sync  
        packet[2] = len(packet) - 3  # Length (37)
        packet[3] = 0x01  # Control packet type
        
        # Update flag
        packet[4] = 0x01
        
        if power is not None:
            packet[5] = 0x80 if power else 0x00
            
        if temp is not None:
            # Temperature control (Bekmansurov encoding)
            temp_val = int(temp - 16)
            if 0 <= temp_val <= 15:
                packet[9] = (packet[9] & 0x0F) | ((temp_val & 0x0F) << 4)
            
        if fan is not None:
            packet[19] = fan & 0x07  # Fan speed 0-5
            
        # Calculate checksum
        packet[39] = self.calc_checksum(packet)
        return packet
        
    def send_control_command(self, packet):
        """Send control command and check response"""
        print(f"Sending control: {packet.hex()}")
        self.ser.write(packet)
        
        time.sleep(0.5)
        
        # Check for immediate response
        response = self.ser.read(200)
        if response:
            print(f"Control response: {response.hex()[:50]}...")
            
        return response
        
    def test_basic_controls(self):
        """Test basic control commands"""
        print("=== UART BIDIRECTIONAL CONTROL TEST ===")
        print(f"Time: {datetime.now()}")
        
        # Get baseline status
        print("\\n1. Getting baseline status...")
        baseline = self.send_query()
        
        if not baseline:
            print("Failed to get baseline status!")
            return
            
        # Test 1: Power control
        print("\\n2. Testing power ON...")
        power_packet = self.create_control_packet(power=True)
        self.send_control_command(power_packet)
        
        time.sleep(1)
        after_power = self.send_query()
        
        # Test 2: Temperature control
        print("\\n3. Testing temperature setpoint...")
        temp_packet = self.create_control_packet(power=True, temp=22)
        self.send_control_command(temp_packet)
        
        time.sleep(1)
        after_temp = self.send_query()
        
        # Test 3: Fan control
        print("\\n4. Testing fan speed...")
        fan_packet = self.create_control_packet(power=True, fan=3)
        self.send_control_command(fan_packet)
        
        time.sleep(1)
        after_fan = self.send_query()
        
        # Compare responses
        print("\\n5. Analyzing responses...")
        if baseline and after_power:
            if baseline != after_power:
                print("✓ System responded to power command!")
            else:
                print("- No change detected after power command")
                
        if after_power and after_temp:
            if after_power != after_temp:
                print("✓ System responded to temperature command!")
            else:
                print("- No change detected after temperature command")
                
        if after_temp and after_fan:
            if after_temp != after_fan:
                print("✓ System responded to fan command!")
            else:
                print("- No change detected after fan command")

def main():
    controller = UARTController()
    
    try:
        controller.connect()
        controller.test_basic_controls()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()

if __name__ == '__main__':
    main()
