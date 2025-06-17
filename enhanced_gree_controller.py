#!/usr/bin/env python3
"""
Enhanced GREE UART Controller
Based on comprehensive protocol research and successful bidirectional tests
"""

import serial
import time
from datetime import datetime

class EnhancedGREEController:
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
            
    def get_status(self):
        """Get current system status"""
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        self.ser.write(query)
        time.sleep(0.3)
        
        response = self.ser.read(500)
        for i in range(len(response) - 10):
            if response[i:i+2] == b'\x7e\x7e' and len(response) > i+2 and response[i+2] == 0xff:
                return response[i:i+255]
        return None
        
    def decode_status(self, packet):
        """Decode status using comprehensive protocol knowledge"""
        if not packet or len(packet) < 64:
            return None
            
        status = {}
        
        # Power (Position 10 = 0xAA means ON)
        if len(packet) > 10:
            status['power'] = packet[10] == 0xAA
            
        # Temperature readings
        if len(packet) > 25:
            status['vapor_temp'] = packet[25]
        if len(packet) > 64:
            status['liquid_temp'] = packet[64]
            
        # Daikin protocol fields that work
        if len(packet) > 8:
            byte8 = packet[8]
            status['mode'] = (byte8 >> 4) & 7  # 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat
            status['fan_speed'] = byte8 & 3
            
        if len(packet) > 9:
            byte9 = packet[9]
            status['set_temp'] = (byte9 >> 4) + 16
            
        if len(packet) > 10:
            byte10 = packet[10]
            status['display_light'] = (byte10 >> 3) & 1
            
        return status
        
    def create_control_packet(self, **kwargs):
        """Create control packet with specified parameters"""
        packet = bytearray(40)
        packet[0] = 0x7e  # Sync
        packet[1] = 0x7e  # Sync
        packet[2] = 0x25  # Length (37 bytes data)
        packet[3] = 0x01  # Control packet type
        
        # Based on your successful tests and evilwombat research:
        
        # Power control
        if 'power' in kwargs:
            if kwargs['power']:
                packet[5] |= 0x80  # Set power bit (byte 5, bit 7)
            packet[4] |= 0x01  # Update flag
            
        # Mode control (Auto=0, Cool=1, Dry=2, Fan=3, Heat=4)
        if 'mode' in kwargs:
            mode = kwargs['mode']
            packet[5] = (packet[5] & 0x8F) | ((mode & 0x07) << 4)
            packet[4] |= 0x01
            
        # Temperature setpoint
        if 'set_temp' in kwargs:
            temp = max(16, min(30, kwargs['set_temp']))  # Clamp to safe range
            temp_encoded = temp - 16  # Subtract 16 as per protocol
            packet[6] = (packet[6] & 0x0F) | ((temp_encoded & 0x0F) << 4)
            packet[4] |= 0x01
            
        # Fan speed (0=Auto, 1=Low, 2=Med, 3=High)
        if 'fan_speed' in kwargs:
            fan = kwargs['fan_speed'] & 0x03
            packet[5] = (packet[5] & 0xFC) | fan
            packet[4] |= 0x01
            
        # Special features
        if 'turbo' in kwargs:
            if kwargs['turbo']:
                packet[8] |= 0x10  # Turbo bit
            packet[4] |= 0x01
            
        if 'xfan' in kwargs:
            if kwargs['xfan']:
                packet[8] |= 0x01  # X-Fan bit
            packet[4] |= 0x01
            
        if 'display_light' in kwargs:
            if kwargs['display_light']:
                packet[8] |= 0x08  # Display light bit
            packet[4] |= 0x01
            
        # Swing control
        if 'swing_vertical' in kwargs:
            swing_v = kwargs['swing_vertical'] & 0x0F
            packet[9] = (packet[9] & 0x0F) | (swing_v << 4)
            packet[4] |= 0x01
            
        if 'swing_horizontal' in kwargs:
            swing_h = kwargs['swing_horizontal'] & 0x0F
            packet[9] = (packet[9] & 0xF0) | swing_h
            packet[4] |= 0x01
        
        # Calculate checksum (sum of data bytes)
        checksum = sum(packet[2:-1]) & 0xFF
        packet[-1] = checksum
        
        return packet
        
    def send_control(self, packet):
        """Send control packet and return response"""
        print(f"Sending control: {packet.hex()}")
        self.ser.write(packet)
        time.sleep(0.5)
        
        response = self.ser.read(500)
        if response:
            print(f"Control response: {response[:50].hex()}...")
            return response
        return None
        
    def set_power(self, on=True):
        """Turn system on/off"""
        packet = self.create_control_packet(power=on)
        return self.send_control(packet)
        
    def set_temperature(self, temp_c):
        """Set temperature setpoint in Celsius"""
        packet = self.create_control_packet(set_temp=temp_c)
        return self.send_control(packet)
        
    def set_mode(self, mode):
        """Set operation mode: 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat"""
        packet = self.create_control_packet(mode=mode)
        return self.send_control(packet)
        
    def set_fan_speed(self, speed):
        """Set fan speed: 0=Auto, 1=Low, 2=Med, 3=High"""
        packet = self.create_control_packet(fan_speed=speed)
        return self.send_control(packet)
        
    def toggle_display_light(self):
        """Toggle display light on/off"""
        # Get current status first
        status_packet = self.get_status()
        if status_packet:
            current_status = self.decode_status(status_packet)
            current_light = current_status.get('display_light', 0)
            new_light = not current_light
            
            packet = self.create_control_packet(display_light=new_light)
            return self.send_control(packet)
        return None
        
    def test_controls_interactive(self):
        """Interactive control testing menu"""
        while True:
            print("\n" + "="*50)
            print("GREE UART Control Test Menu")
            print("="*50)
            
            # Show current status
            status_packet = self.get_status()
            if status_packet:
                status = self.decode_status(status_packet)
                if status:
                    modes = ['Auto', 'Cool', 'Dry', 'Fan', 'Heat']
                    mode_name = modes[status.get('mode', 0)]
                    
                    print(f"Current Status:")
                    print(f"  Power: {'ON' if status.get('power') else 'OFF'}")
                    print(f"  Mode: {mode_name}")
                    print(f"  Set Temp: {status.get('set_temp', '?')}°C")
                    print(f"  Fan Speed: {status.get('fan_speed', '?')}")
                    print(f"  Vapor Temp: {status.get('vapor_temp', '?')}°C")
                    print(f"  Liquid Temp: {status.get('liquid_temp', '?')}°C")
                    print(f"  Display Light: {'ON' if status.get('display_light') else 'OFF'}")
            
            print(f"\nAvailable Commands:")
            print(f"  1. Power ON/OFF")
            print(f"  2. Set Temperature")
            print(f"  3. Set Mode")
            print(f"  4. Set Fan Speed")
            print(f"  5. Toggle Display Light")
            print(f"  6. Show Status Only")
            print(f"  9. Exit")
            
            choice = input("\nEnter choice (1-6, 9): ").strip()
            
            if choice == '1':
                power = input("Power (on/off): ").strip().lower()
                self.set_power(power == 'on')
                
            elif choice == '2':
                try:
                    temp = int(input("Temperature (16-30°C): "))
                    self.set_temperature(temp)
                except ValueError:
                    print("Invalid temperature")
                    
            elif choice == '3':
                print("Modes: 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat")
                try:
                    mode = int(input("Mode (0-4): "))
                    self.set_mode(mode)
                except ValueError:
                    print("Invalid mode")
                    
            elif choice == '4':
                print("Fan: 0=Auto, 1=Low, 2=Med, 3=High")
                try:
                    fan = int(input("Fan speed (0-3): "))
                    self.set_fan_speed(fan)
                except ValueError:
                    print("Invalid fan speed")
                    
            elif choice == '5':
                self.toggle_display_light()
                
            elif choice == '6':
                continue  # Just show status again
                
            elif choice == '9':
                break
                
            else:
                print("Invalid choice")
            
            time.sleep(1)  # Wait before next status update

def main():
    controller = EnhancedGREEController()
    
    try:
        controller.connect()
        print("Enhanced GREE UART Controller Ready")
        controller.test_controls_interactive()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()

if __name__ == '__main__':
    main()
