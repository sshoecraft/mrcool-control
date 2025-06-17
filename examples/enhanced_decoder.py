#!/usr/bin/env python3
"""
Enhanced Real-time Decoder
Real-time UART monitoring with protocol analysis
"""

import serial
import time
from datetime import datetime

class EnhancedDecoder:
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
            
    def find_sync_pattern(self, buffer):
        """Find 7E7E sync pattern in buffer"""
        return buffer.find(b'\\x7e\\x7e')
    
    def decode_packet(self, packet):
        """Decode packet using known methods"""
        if len(packet) < 5:
            return None
            
        result = {
            'timestamp': datetime.now(),
            'length': len(packet),
            'type': f'0x{packet[3]:02x}' if len(packet) > 3 else 'Unknown'
        }
        
        # Temperature positions for Mr Cool
        if len(packet) > 64:
            result['liquid_temp'] = packet[64]
        if len(packet) > 25:
            result['vapor_temp'] = packet[25]
        if len(packet) > 31:
            result['operational'] = packet[31]
            
        # Bekmansurov style decoding
        if len(packet) > 8:
            byte8 = packet[8]
            result['power'] = (byte8 >> 7) & 1
            result['mode'] = (byte8 >> 4) & 7
            
        if len(packet) > 9:
            byte9 = packet[9]
            temp_raw = (byte9 >> 4) & 0x0F
            result['set_temp'] = temp_raw + 16
            
        return result
        
    def print_decoded(self, decoded, count):
        """Print decoded packet info"""
        timestamp = decoded['timestamp'].strftime('%H:%M:%S.%f')[:-3]
        
        print(f"\\n[{count}] {timestamp} - Type: {decoded['type']}, Length: {decoded['length']}")
        
        if 'power' in decoded:
            power_status = "ON" if decoded['power'] else "OFF"
            print(f"  Power: {power_status}")
            
        if 'mode' in decoded:
            modes = ['Auto', 'Cool', 'Dry', 'Fan', 'Heat']
            mode_name = modes[decoded['mode']] if 0 <= decoded['mode'] < len(modes) else 'Unknown'
            print(f"  Mode: {mode_name}")
            
        if 'set_temp' in decoded:
            print(f"  Set Temp: {decoded['set_temp']}°C")
            
        if 'liquid_temp' in decoded and 'vapor_temp' in decoded:
            liquid = decoded['liquid_temp']
            vapor = decoded['vapor_temp']
            diff = liquid - vapor
            print(f"  Refrigerant: Liquid={liquid}°C, Vapor={vapor}°C (Δ{diff}°C)")
            
        if 'operational' in decoded:
            print(f"  Operational: {decoded['operational']}")
    
    def monitor(self, duration=None):
        """Monitor UART traffic continuously"""
        if not self.ser:
            print("Not connected")
            return
            
        print("Real-time UART Monitor (Ctrl+C to stop)")
        print("=" * 50)
        
        buffer = b''
        start_time = time.time()
        packet_count = 0
        
        try:
            while duration is None or (time.time() - start_time) < duration:
                # Read data
                data = self.ser.read(self.ser.in_waiting or 100)
                if data:
                    buffer += data
                
                # Process packets
                while len(buffer) >= 5:
                    sync_pos = self.find_sync_pattern(buffer)
                    
                    if sync_pos == -1:
                        buffer = b''
                        break
                    
                    if sync_pos > 0:
                        buffer = buffer[sync_pos:]
                    
                    if len(buffer) < 3:
                        break
                    
                    expected_size = buffer[2] + 3
                    
                    if len(buffer) < expected_size:
                        break
                    
                    # Extract and decode packet
                    packet = buffer[:expected_size]
                    buffer = buffer[expected_size:]
                    
                    decoded = self.decode_packet(packet)
                    if decoded:
                        packet_count += 1
                        self.print_decoded(decoded, packet_count)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\\nStopped. Processed {packet_count} packets.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced UART Decoder')
    parser.add_argument('--port', default='/dev/serial0', help='Serial port')
    parser.add_argument('--baud', type=int, default=9600, help='Baud rate')
    parser.add_argument('--duration', type=int, help='Monitor duration in seconds')
    
    args = parser.parse_args()
    
    decoder = EnhancedDecoder(args.port, args.baud)
    
    try:
        if decoder.connect():
            decoder.monitor(args.duration)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        decoder.disconnect()

if __name__ == '__main__':
    main()
