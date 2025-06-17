#!/usr/bin/env python3
"""
Enhanced Gree Data Collector
Uses comprehensive protocol understanding from research documentation
"""

import serial
import time
import csv
import json
from datetime import datetime

class EnhancedGreeCollector:
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
            
    def get_status_packet(self):
        """Get clean status packet from system"""
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        self.ser.write(query)
        time.sleep(0.3)
        
        response = self.ser.read(500)
        
        # Find complete 7e7e packet
        for i in range(len(response) - 10):
            if (response[i:i+2] == b'\x7e\x7e' and 
                len(response) > i+2 and response[i+2] == 0xff):
                # Found 255-byte packet
                end_pos = min(i + 258, len(response))
                return response[i:end_pos]
        return None
        
    def decode_comprehensive(self, packet):
        """Enhanced decode using all research findings"""
        if not packet or len(packet) < 50:
            return None
            
        result = {
            'timestamp': datetime.now().isoformat(),
            'packet_length': len(packet),
            'raw_hex': packet.hex(),
        }
        
        # Header analysis
        if packet[0:2] == b'\x7e\x7e':
            result['payload_size'] = packet[2]
            result['packet_type'] = f'0x{packet[3]:02x}'
            result['device_addr'] = f'0x{packet[4]:02x}'
        
        # Daikin protocol insights
        if len(packet) > 8:
            byte8 = packet[8]
            result['power_state'] = (byte8 >> 7) & 1
            result['mode'] = (byte8 >> 4) & 7
            result['fan_speed'] = byte8 & 3
            
        if len(packet) > 9:
            byte9 = packet[9]
            result['set_temp_daikin'] = (byte9 >> 4) + 16
            
        if len(packet) > 10:
            byte10 = packet[10]
            result['turbo'] = (byte10 >> 4) & 1
            result['display_light'] = (byte10 >> 3) & 1
            result['xfan'] = byte10 & 1
            
        # Bekmansurov temperature analysis
        if len(packet) > 9:
            byte9 = packet[9]
            temp_raw = (byte9 >> 4) & 0x0F
            result['set_temp_bekmansurov'] = temp_raw + 16
            
        if len(packet) > 13:
            byte13 = packet[13]
            result['temp_half_increment'] = (byte13 >> 3) & 1
            
        # Mr Cool specific temperature positions
        temp_positions = [25, 31, 64]
        for pos in temp_positions:
            if len(packet) > pos:
                val = packet[pos]
                result[f'temp_pos{pos}'] = val
                result[f'temp_pos{pos}_f'] = val * 9/5 + 32
                
                # Internal room temp (subtract 40)
                internal_temp = val - 40
                if 10 <= internal_temp <= 35:
                    result[f'room_temp_pos{pos}'] = internal_temp
        
        # Mode interpretation
        mode_names = ['Auto', 'Cool', 'Dry', 'Fan', 'Heat']
        if 'mode' in result:
            mode_val = result['mode']
            result['mode_name'] = mode_names[mode_val] if 0 <= mode_val < len(mode_names) else f'Unknown({mode_val})'
            
        # Calculate effective set temperature
        if 'set_temp_bekmansurov' in result and 'temp_half_increment' in result:
            effective_temp = result['set_temp_bekmansurov']
            if result['temp_half_increment']:
                effective_temp += 0.5
            result['effective_set_temp'] = effective_temp
            
        return result
        
    def monitor_continuous(self, duration_minutes=5, interval_seconds=2, output_file=None):
        """Continuous monitoring with enhanced protocol analysis"""
        
        if output_file is None:
            output_file = f"enhanced_gree_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # CSV setup
        csv_file = open(output_file, 'w', newline='')
        fieldnames = [
            'timestamp', 'elapsed_seconds', 'packet_length', 'packet_type',
            'power_state', 'mode', 'mode_name', 'fan_speed',
            'set_temp_daikin', 'set_temp_bekmansurov', 'effective_set_temp',
            'temp_pos25', 'temp_pos31', 'temp_pos64',
            'room_temp_pos31', 'turbo', 'xfan', 'display_light',
            'temp_pos25_f', 'temp_pos31_f', 'temp_pos64_f', 'raw_hex'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        print(f"Enhanced monitoring started - Duration: {duration_minutes} min, Interval: {interval_seconds}s")
        print(f"Output file: {output_file}")
        print("-" * 80)
        
        sample_count = 0
        
        try:
            while time.time() < end_time:
                packet = self.get_status_packet()
                
                if packet:
                    analysis = self.decode_comprehensive(packet)
                    
                    if analysis:
                        # Add elapsed time
                        analysis['elapsed_seconds'] = round(time.time() - start_time, 1)
                        
                        # Write to CSV
                        writer.writerow(analysis)
                        csv_file.flush()
                        
                        sample_count += 1
                        
                        # Real-time display (every 10th sample)
                        if sample_count % 5 == 0:
                            print(f"Sample {sample_count:3d} | "
                                  f"Power: {'ON' if analysis.get('power_state') else 'OFF':3s} | "
                                  f"Mode: {analysis.get('mode_name', 'Unknown'):4s} | "
                                  f"Temp: Pos25={analysis.get('temp_pos25', '?'):2s}°C "
                                  f"Pos31={analysis.get('temp_pos31', '?'):2s}°C "
                                  f"Pos64={analysis.get('temp_pos64', '?'):2s}°C | "
                                  f"Features: {'T' if analysis.get('turbo') else '-'}"
                                  f"{'X' if analysis.get('xfan') else '-'}"
                                  f"{'D' if analysis.get('display_light') else '-'}")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\nMonitoring stopped by user after {sample_count} samples")
        
        finally:
            csv_file.close()
            print(f"Data saved to: {output_file}")
            print(f"Total samples collected: {sample_count}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Gree HVAC Data Collector")
    parser.add_argument("--duration", type=float, default=5, help="Duration in minutes")
    parser.add_argument("--interval", type=float, default=2, help="Interval in seconds")
    parser.add_argument("--output", help="Output CSV file name")
    
    args = parser.parse_args()
    
    collector = EnhancedGreeCollector()
    
    try:
        collector.connect()
        collector.monitor_continuous(args.duration, args.interval, args.output)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        collector.disconnect()

if __name__ == '__main__':
    main()
