#!/usr/bin/env python3
\"\"\"
Comprehensive GREE Protocol Decoder
Combines Bekmansurov, evilwombat, and Daikin insights for Mr Cool system
\"\"\"

import serial
import time
from datetime import datetime

class ComprehensiveGREEDecoder:
    def __init__(self, port='/dev/serial0', baud=9600):
        self.port = port
        self.baud = baud
        self.ser = None
        
    def connect(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        print(f\"Connected to {self.port}\")
        
    def disconnect(self):
        if self.ser:
            self.ser.close()
            
    def get_status_packet(self):
        \"\"\"Get clean status packet from system\"\"\"
        query = bytearray([0x7e, 0x7e, 0x02, 0x02, 0x04])
        self.ser.write(query)
        time.sleep(0.3)
        
        response = self.ser.read(500)
        
        # Find complete 7e7e packet
        for i in range(len(response) - 10):
            if (response[i:i+2] == b'\\x7e\\x7e' and 
                len(response) > i+2 and response[i+2] == 0xff):
                # Found 255-byte packet
                end_pos = min(i + 258, len(response))  # 255 + 3 header
                return response[i:end_pos]
        return None
        
    def decode_comprehensive(self, packet):
        \"\"\"Decode using all known protocol insights\"\"\"
        if not packet or len(packet) < 50:
            return None
            
        result = {
            'timestamp': datetime.now(),
            'packet_length': len(packet),
            'header': packet[:5].hex(),
        }
        
        # Header analysis
        if packet[0:2] == b'\\x7e\\x7e':
            result['sync'] = 'OK'
            result['payload_size'] = packet[2]
            result['packet_type'] = f'0x{packet[3]:02x}'
            result['device_addr'] = f'0x{packet[4]:02x}'
        
        # Apply different decoding methods
        result.update(self.decode_mr_cool_specific(packet))
        result.update(self.decode_bekmansurov_style(packet))
        
        return result
        
    def decode_bekmansurov_style(self, packet):
        \"\"\"Apply Bekmansurov research findings\"\"\"
        result = {}
        
        # Bekmansurov byte 8: power + mode
        if len(packet) > 8:
            byte8 = packet[8]
            result['bekmansurov_power'] = (byte8 >> 7) & 1
            result['bekmansurov_mode'] = (byte8 >> 4) & 7
            
        # Bekmansurov byte 9: temperature (upper 4 bits, C-16)
        if len(packet) > 9:
            byte9 = packet[9]
            temp_raw = (byte9 >> 4) & 0x0F
            result['bekmansurov_temp'] = temp_raw + 16
            
        return result
        
    def decode_mr_cool_specific(self, packet):
        \"\"\"Apply Mr Cool MDUO18060 specific observations\"\"\"
        result = {}
        
        # Our observed temperature candidate positions
        temp_positions = [25, 31, 64]
        for pos in temp_positions:
            if len(packet) > pos:
                val = packet[pos]
                result[f'temp_pos_{pos}_c'] = val
                result[f'temp_pos_{pos}_f'] = val * 9/5 + 32
                    
        return result
        
    def print_analysis(self, analysis):
        \"\"\"Pretty print comprehensive analysis\"\"\"
        if not analysis:
            print(\"No analysis data\")
            return
            
        print(\"=\" * 60)
        print(f\"COMPREHENSIVE GREE ANALYSIS - {analysis['timestamp'].strftime('%H:%M:%S')}\")
        print(\"=\" * 60)
        
        # Header info
        print(f\"Packet: {analysis['packet_length']} bytes, {analysis['header']}\")
        print(f\"Type: {analysis.get('packet_type', 'Unknown')}, Device: {analysis.get('device_addr', 'Unknown')}\")
        
        # Power and mode analysis
        print(f\"\\nPOWER & MODE ANALYSIS:\")
        if 'bekmansurov_power' in analysis:
            status = \"ON\" if analysis['bekmansurov_power'] else \"OFF\"
            print(f\"  Power: {status}\")
            
        if 'bekmansurov_mode' in analysis:
            modes = ['Auto', 'Cool', 'Dry', 'Fan', 'Heat']
            mode_val = analysis['bekmansurov_mode']
            mode_name = modes[mode_val] if 0 <= mode_val < len(modes) else f'Unknown({mode_val})'
            print(f\"  Mode: {mode_name}\")
        
        # Temperature analysis
        print(f\"\\nTEMPERATURE ANALYSIS:\")
        
        if 'bekmansurov_temp' in analysis:
            print(f\"  Set temp: {analysis['bekmansurov_temp']}°C\")
            
        # Mr Cool temperature positions
        for pos in [25, 31, 64]:
            temp_key = f'temp_pos_{pos}_c'
            if temp_key in analysis:
                temp_c = analysis[temp_key]
                temp_f = analysis[f'temp_pos_{pos}_f']
                print(f\"  Position {pos}: {temp_c}°C ({temp_f:.1f}°F)\")

def main():
    decoder = ComprehensiveGREEDecoder()
    
    try:
        decoder.connect()
        
        print(\"Getting comprehensive system analysis...\")
        packet = decoder.get_status_packet()
        
        if packet:
            analysis = decoder.decode_comprehensive(packet)
            decoder.print_analysis(analysis)
        else:
            print(\"Failed to get status packet\")
            
    except Exception as e:
        print(f\"Error: {e}\")
    finally:
        decoder.disconnect()

if __name__ == '__main__':
    main()
