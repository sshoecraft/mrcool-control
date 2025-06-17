#!/usr/bin/env python3
"""
Interactive Packet Analyzer
Analyze GREE HVAC protocol packets with multiple decoding methods
"""

import sys
from datetime import datetime

class PacketAnalyzer:
    def __init__(self):
        self.mode_map = {
            0: "Auto", 1: "Cool", 2: "Dry", 3: "Fan", 4: "Heat"
        }
    
    def parse_hex_input(self, hex_string):
        """Parse hex string input into bytes"""
        # Remove spaces, newlines, and common prefixes
        cleaned = hex_string.replace(' ', '').replace('\\n', '').replace('0x', '')
        
        try:
            return bytes.fromhex(cleaned)
        except ValueError as e:
            print(f"Error parsing hex string: {e}")
            return None
    
    def analyze_header(self, packet):
        """Analyze packet header"""
        if len(packet) < 5:
            return None
            
        if packet[0:2] != b'\\x7e\\x7e':
            return {"error": "Invalid sync pattern"}
            
        return {
            'sync': packet[0:2].hex(),
            'payload_size': packet[2],
            'packet_type': f'0x{packet[3]:02x}',
            'device_addr': f'0x{packet[4]:02x}',
            'total_length': len(packet)
        }
    
    def decode_bekmansurov_style(self, packet):
        """Apply Bekmansurov research findings"""
        result = {}
        
        # Bekmansurov byte 8: power + mode
        if len(packet) > 8:
            byte8 = packet[8]
            result['power'] = (byte8 >> 7) & 1
            result['mode'] = (byte8 >> 4) & 7
            result['mode_name'] = self.mode_map.get(result['mode'], 'Unknown')
            
        # Bekmansurov byte 9: temperature (upper 4 bits, C-16)
        if len(packet) > 9:
            byte9 = packet[9]
            temp_raw = (byte9 >> 4) & 0x0F
            result['set_temp_c'] = temp_raw + 16
            result['set_temp_f'] = result['set_temp_c'] * 9/5 + 32
            
        # Bekmansurov byte 12: swing mode
        if len(packet) > 12:
            byte12 = packet[12]
            result['swing_v'] = (byte12 >> 4) & 0x0F
            result['swing_h'] = byte12 & 0x0F
            
        # Bekmansurov byte 13: temperature 0.5 increment
        if len(packet) > 13:
            byte13 = packet[13]
            result['temp_half_degree'] = (byte13 >> 3) & 1
            if result.get('set_temp_c') and result['temp_half_degree']:
                result['set_temp_c'] += 0.5
                result['set_temp_f'] = result['set_temp_c'] * 9/5 + 32
            
        return result
    
    def decode_mr_cool_specific(self, packet):
        """Apply Mr Cool MDUO18060 specific observations"""
        result = {}
        
        # Temperature candidate positions
        temp_positions = [25, 31, 64]
        for pos in temp_positions:
            if len(packet) > pos:
                val = packet[pos]
                result[f'temp_pos_{pos}'] = {
                    'celsius': val,
                    'fahrenheit': val * 9/5 + 32,
                    'raw_value': f'0x{val:02x}'
                }
        
        # Operational byte
        if len(packet) > 31:
            result['operational_byte'] = {
                'value': packet[31],
                'hex': f'0x{packet[31]:02x}'
            }
            
        return result
    
    def decode_control_positions(self, packet):
        """Decode discovered control positions"""
        result = {}
        
        if len(packet) < 40:
            return result
            
        # Control positions discovered in research
        positions = {
            5: 'power_control',
            6: 'compressor_capacity', 
            7: 'refrigerant_flow',
            8: 'heat_cool_mode',
            19: 'fan_speed'
        }
        
        for pos, name in positions.items():
            if len(packet) > pos:
                val = packet[pos]
                result[name] = {
                    'value': val,
                    'hex': f'0x{val:02x}',
                    'position': pos
                }
                
        return result
    
    def print_analysis(self, packet):
        """Print comprehensive packet analysis"""
        print("=" * 70)
        print(f"PACKET ANALYSIS - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        
        # Header analysis
        header = self.analyze_header(packet)
        if header:
            if 'error' in header:
                print(f"❌ {header['error']}")
                return
                
            print(f"📦 HEADER INFO:")
            print(f"   Sync: {header['sync']}")
            print(f"   Payload Size: {header['payload_size']} bytes")
            print(f"   Packet Type: {header['packet_type']}")
            print(f"   Device Address: {header['device_addr']}")
            print(f"   Total Length: {header['total_length']} bytes")
        
        # Bekmansurov analysis
        bekmansurov = self.decode_bekmansurov_style(packet)
        if bekmansurov:
            print(f"\\n🔬 BEKMANSUROV ANALYSIS:")
            if 'power' in bekmansurov:
                status = "ON" if bekmansurov['power'] else "OFF"
                print(f"   Power: {status}")
            if 'mode_name' in bekmansurov:
                print(f"   Mode: {bekmansurov['mode_name']}")
            if 'set_temp_c' in bekmansurov:
                print(f"   Set Temperature: {bekmansurov['set_temp_c']}°C ({bekmansurov['set_temp_f']:.1f}°F)")
            if 'swing_v' in bekmansurov or 'swing_h' in bekmansurov:
                print(f"   Swing: V={bekmansurov.get('swing_v', '?')} H={bekmansurov.get('swing_h', '?')}")
        
        # Mr Cool specific
        mr_cool = self.decode_mr_cool_specific(packet)
        if mr_cool:
            print(f"\\n🌡️  MR COOL TEMPERATURE POSITIONS:")
            for key, data in mr_cool.items():
                if key.startswith('temp_pos_'):
                    pos = key.split('_')[2]
                    print(f"   Position {pos}: {data['celsius']}°C ({data['fahrenheit']:.1f}°F) [{data['raw_value']}]")
            
            if 'operational_byte' in mr_cool:
                op = mr_cool['operational_byte']
                print(f"   Operational Byte: {op['value']} [{op['hex']}]")
        
        # Control positions (for 40-byte control packets)
        if len(packet) >= 40:
            controls = self.decode_control_positions(packet)
            if controls:
                print(f"\\n⚡ CONTROL POSITIONS:")
                for name, data in controls.items():
                    print(f"   {name.replace('_', ' ').title()}: {data['value']} [{data['hex']}] @ pos {data['position']}")
        
        # Raw data preview
        print(f"\\n📄 RAW DATA (first 32 bytes):")
        hex_data = packet[:32].hex()
        formatted_hex = ' '.join([hex_data[i:i+2] for i in range(0, len(hex_data), 2)])
        print(f"   {formatted_hex}")
        
        if len(packet) > 32:
            print(f"   ... ({len(packet) - 32} more bytes)")

def main():
    analyzer = PacketAnalyzer()
    
    if len(sys.argv) > 1:
        # Packet provided as command line argument
        hex_input = ' '.join(sys.argv[1:])
        packet = analyzer.parse_hex_input(hex_input)
        if packet:
            analyzer.print_analysis(packet)
    else:
        # Interactive mode
        print("🔍 Interactive Packet Analyzer")
        print("Enter hex packet data (or 'quit' to exit):")
        print("Example: 7e7effe0013c3027020b5500...")
        
        while True:
            try:
                hex_input = input("\\nPacket> ").strip()
                
                if hex_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not hex_input:
                    continue
                    
                packet = analyzer.parse_hex_input(hex_input)
                if packet:
                    analyzer.print_analysis(packet)
                    
            except KeyboardInterrupt:
                print("\\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()
