#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu Health Monitor - API Test Script
ทดสอบการทำงานของ API และแสดงผลลัพธ์
"""

import json
import requests
import argparse
import sys
from datetime import datetime

def format_bytes(bytes_value):
    """แปลงหน่วย bytes เป็น KB, MB, GB"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024**2:
        return f"{bytes_value/1024:.2f} KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value/(1024**2):.2f} MB"
    else:
        return f"{bytes_value/(1024**3):.2f} GB"

def print_header(title):
    """พิมพ์หัวข้อ"""
    width = 60
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)

def test_api(base_url, endpoint):
    """ทดสอบ API endpoint และแสดงผลลัพธ์"""
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling {url}: {str(e)}")
        return None

def print_system_info(data):
    """แสดงข้อมูลระบบ"""
    print_header("System Information")
    
    system = data["system"]
    print(f"Hostname:  {system['hostname']}")
    print(f"Platform:  {system['platform']}")
    print(f"Kernel:    {system['kernel']}")
    print(f"Uptime:    {system['uptime']['formatted']}")
    print(f"Timestamp: {datetime.fromisoformat(system['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

def print_cpu_info(data):
    """แสดงข้อมูล CPU"""
    print_header("CPU Information")
    
    cpu = data["cpu"]
    print(f"Model:       {cpu['model']}")
    print(f"Usage:       {cpu['percent']}%")
    print(f"Cores:       {cpu['cores']['physical']} physical, {cpu['cores']['logical']} logical")
    
    if cpu['frequency']['current']:
        print(f"Frequency:   {cpu['frequency']['current']:.2f} MHz")
    
    print("Load Average:")
    print(f"  1 min:     {cpu['load_average']['1min']:.2f}")
    print(f"  5 min:     {cpu['load_average']['5min']:.2f}")
    print(f"  15 min:    {cpu['load_average']['15min']:.2f}")

def print_memory_info(data):
    """แสดงข้อมูล Memory"""
    print_header("Memory Information")
    
    mem = data["memory"]["ram"]
    swap = data["memory"]["swap"]
    
    print("RAM:")
    print(f"  Total:     {format_bytes(mem['total'])}")
    print(f"  Used:      {format_bytes(mem['used'])} ({mem['percent']}%)")
    print(f"  Available: {format_bytes(mem['available'])}")
    
    print("\nSwap:")
    print(f"  Total:     {format_bytes(swap['total'])}")
    print(f"  Used:      {format_bytes(swap['used'])} ({swap['percent']}%)")
    print(f"  Free:      {format_bytes(swap['free'])}")

def print_disk_info(data):
    """แสดงข้อมูล Disk"""
    print_header("Disk Information")
    
    partitions = data["disk"]["partitions"]
    
    print("Partitions:")
    for part in partitions:
        print(f"  {part['device']} ({part['mountpoint']}, {part['fstype']}):")
        print(f"    Total:   {format_bytes(part['total'])}")
        print(f"    Used:    {format_bytes(part['used'])} ({part['percent']}%)")
        print(f"    Free:    {format_bytes(part['free'])}")
    
    if data["disk"]["io"]:
        io = data["disk"]["io"]
        print("\nDisk I/O:")
        print(f"  Read:     {io['read_count']} operations, {format_bytes(io['read_bytes'])}")
        print(f"  Write:    {io['write_count']} operations, {format_bytes(io['write_bytes'])}")

def print_network_info(data):
    """แสดงข้อมูล Network"""
    print_header("Network Information")
    
    interfaces = data["network"]["interfaces"]
    
    print("Interfaces:")
    for name, interface in interfaces.items():
        print(f"  {name}:")
        
        for addr in interface["addresses"]:
            if addr["family"] == "2":  # IPv4
                print(f"    IPv4:      {addr['address']}")
                if addr["netmask"]:
                    print(f"    Netmask:    {addr['netmask']}")
                if addr["broadcast"]:
                    print(f"    Broadcast:  {addr['broadcast']}")
            elif addr["family"] == "17":  # IPv6
                print(f"    IPv6:      {addr['address']}")
        
        if "io" in interface:
            io = interface["io"]
            print(f"    Sent:       {format_bytes(io['bytes_sent'])}")
            print(f"    Received:   {format_bytes(io['bytes_recv'])}")
            print(f"    Packets:    {io['packets_sent']} sent, {io['packets_recv']} received")
            if io['errin'] > 0 or io['errout'] > 0:
                print(f"    Errors:     {io['errin']} in, {io['errout']} out")
            if io['dropin'] > 0 or io['dropout'] > 0:
                print(f"    Dropped:    {io['dropin']} in, {io['dropout']} out")
    
    if data["network"]["connections"]:
        conn = data["network"]["connections"]
        print("\nConnections:")
        print(f"  Established: {conn['established']}")
        print(f"  Listen:      {conn['listen']}")
        print(f"  Time Wait:   {conn['time_wait']}")
        print(f"  Close Wait:  {conn['close_wait']}")
        print(f"  Other:       {conn['other']}")

def print_temperature_info(data):
    """แสดงข้อมูลอุณหภูมิ"""
    print_header("Temperature Information")
    
    temps = data["temperature"]
    
    if isinstance(temps, dict) and "error" in temps:
        print(f"Error: {temps['error']}")
        return
    
    for chip, sensors in temps.items():
        print(f"Chip: {chip}")
        
        if isinstance(sensors, list):
            for sensor in sensors:
                label = sensor.get('label', 'Unknown')
                current = sensor.get('current')
                high = sensor.get('high')
                critical = sensor.get('critical')
                
                print(f"  {label}:")
                if current is not None:
                    print(f"    Current:  {current}°C")
                if high is not None:
                    print(f"    High:     {high}°C")
                if critical is not None:
                    print(f"    Critical: {critical}°C")
        else:
            # Handle different format
            for sensor_name, sensor_data in sensors.items():
                print(f"  {sensor_name}:")
                
                if isinstance(sensor_data, dict):
                    for key, value in sensor_data.items():
                        if isinstance(value, (int, float)):
                            print(f"    {key}: {value}°C")
                        elif isinstance(value, dict) and 'input' in value:
                            print(f"    {key}: {value['input']}°C")

def print_ai_summary(data):
    """แสดงสรุปข้อมูลจาก AI"""
    print_header("AI System Analysis")
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(data["summary"])
    print(f"\nAnalysis timestamp: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    parser = argparse.ArgumentParser(description="Test Ubuntu Health Monitor API")
    parser.add_argument("--host", default="localhost", help="API host (default: localhost)")
    parser.add_argument("--port", default=5000, type=int, help="API port (default: 5000)")
    parser.add_argument("--endpoint", default="/api/v1/system/info", 
                        help="API endpoint to test (default: /api/v1/system/info)")
    parser.add_argument("--summary", action="store_true", help="Get AI summary of system status")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    if args.summary:
        endpoint = "/api/v1/system/summary"
    else:
        endpoint = args.endpoint
    
    print(f"Testing {base_url}{endpoint}...")
    result = test_api(base_url, endpoint)
    
    if result is None:
        print("Failed to get data from API")
        sys.exit(1)
    
    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    if args.summary:
        print_ai_summary(result)
    elif endpoint == "/api/v1/system/info":
        print_system_info(result)
        print_cpu_info(result)
        print_memory_info(result)
        print_disk_info(result)
        print_network_info(result)
        print_temperature_info(result)
    elif endpoint == "/api/v1/system/cpu":
        print_cpu_info({"cpu": result})
    elif endpoint == "/api/v1/system/memory":
        print_memory_info({"memory": result})
    elif endpoint == "/api/v1/system/disk":
        print_disk_info({"disk": result})
    elif endpoint == "/api/v1/system/network":
        print_network_info({"network": result})
    elif endpoint == "/api/v1/system/temperature":
        print_temperature_info({"temperature": result})
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
