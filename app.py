#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu Health Monitor - Flask API

ระบบติดตามและวิเคราะห์สถานะเซิร์ฟเวอร์ Ubuntu แบบเรียลไทม์
"""

import os
import json
import logging
import platform
import psutil
import requests
import subprocess
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import openai

# ตั้งค่า logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# โหลดการตั้งค่า
try:
    with open('config/settings.json', 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    logging.error("ไม่พบไฟล์ settings.json")
    settings = {
        "openai": {"api_key": "", "model": "gpt-4"},
        "discord": {"webhook_url": ""},
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "my-token",
            "org": "my-org",
            "bucket": "system_metrics"
        }
    }

try:
    with open('config/thresholds.json', 'r') as f:
        thresholds = json.load(f)
except FileNotFoundError:
    logging.error("ไม่พบไฟล์ thresholds.json")
    thresholds = {
        "cpu_percent": 80,
        "memory_percent": 85,
        "disk_percent": 90,
        "temperature": 70
    }

# ตั้งค่า OpenAI API
if settings["openai"]["api_key"]:
    openai.api_key = settings["openai"]["api_key"]

# ตั้งค่า InfluxDB client
influxdb_client = InfluxDBClient(
    url=settings["influxdb"]["url"],
    token=settings["influxdb"]["token"],
    org=settings["influxdb"]["org"]
)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

# โหลด system prompt
try:
    with open('prompts/system_summary_prompt.txt', 'r') as f:
        system_summary_prompt = f.read()
except FileNotFoundError:
    logging.warning("ไม่พบไฟล์ system_summary_prompt.txt")
    system_summary_prompt = """
    คุณเป็น AI ผู้เชี่ยวชาญด้านการวิเคราะห์ระบบ Linux/Ubuntu
    วิเคราะห์ข้อมูลระบบต่อไปนี้และให้สรุปสถานะและคำแนะนำ:
    {system_data}
    
    โปรดวิเคราะห์:
    1. สถานะทั่วไปของระบบ
    2. ปัญหาที่พบหรืออาจเกิดขึ้น
    3. คำแนะนำในการแก้ไขหรือปรับปรุง
    4. ทรัพยากรใดที่อาจต้องได้รับการอัปเกรด
    """

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/system/info', methods=['GET'])
def get_system_info():
    """ข้อมูลระบบทั้งหมด"""
    data = {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
        "temperature": get_temperature_info(),
        "system": {
            "platform": platform.platform(),
            "hostname": platform.node(),
            "kernel": platform.release(),
            "uptime": get_uptime(),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # เก็บข้อมูลลง InfluxDB
    try:
        store_in_influxdb(data)
    except Exception as e:
        logging.error(f"ไม่สามารถบันทึกข้อมูลลง InfluxDB: {str(e)}")
    
    # ตรวจสอบ thresholds และส่งการแจ้งเตือนถ้าจำเป็น
    check_thresholds(data)
    
    return jsonify(data)

@app.route('/api/v1/system/cpu', methods=['GET'])
def get_cpu_endpoint():
    """ข้อมูล CPU"""
    return jsonify(get_cpu_info())

@app.route('/api/v1/system/memory', methods=['GET'])
def get_memory_endpoint():
    """ข้อมูล Memory"""
    return jsonify(get_memory_info())

@app.route('/api/v1/system/disk', methods=['GET'])
def get_disk_endpoint():
    """ข้อมูล Disk"""
    return jsonify(get_disk_info())

@app.route('/api/v1/system/network', methods=['GET'])
def get_network_endpoint():
    """ข้อมูล Network"""
    return jsonify(get_network_info())

@app.route('/api/v1/system/temperature', methods=['GET'])
def get_temperature_endpoint():
    """ข้อมูลอุณหภูมิ"""
    return jsonify(get_temperature_info())

@app.route('/api/v1/system/summary', methods=['GET'])
def get_ai_summary():
    """สรุปสถานะระบบด้วย AI"""
    if not settings["openai"]["api_key"]:
        return jsonify({"error": "OpenAI API key ไม่ได้ถูกตั้งค่า"}), 500
    
    # ดึงข้อมูลระบบ
    system_data = {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "temperature": get_temperature_info(),
        "uptime": get_uptime()
    }
    
    try:
        # สร้าง prompt
        prompt = system_summary_prompt.format(system_data=json.dumps(system_data, indent=2))
        
        # เรียกใช้ OpenAI API
        response = openai.ChatCompletion.create(
            model=settings["openai"]["model"],
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "วิเคราะห์สถานะระบบปัจจุบัน"}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        summary = response.choices[0].message.content
        
        return jsonify({
            "summary": summary,
            "system_data": system_data,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logging.error(f"ไม่สามารถวิเคราะห์ข้อมูลด้วย OpenAI: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_cpu_info():
    """ดึงข้อมูล CPU"""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    load_avg = os.getloadavg()
    
    try:
        # ดึงข้อมูล CPU จาก lscpu
        cpu_info = subprocess.check_output(['lscpu'], text=True)
        cpu_model = ""
        
        for line in cpu_info.split('\n'):
            if 'Model name' in line:
                cpu_model = line.split(':')[1].strip()
                break
    except:
        cpu_model = "Unknown"
    
    return {
        "percent": cpu_percent,
        "cores": {
            "physical": psutil.cpu_count(logical=False),
            "logical": psutil.cpu_count(logical=True)
        },
        "frequency": {
            "current": cpu_freq.current if cpu_freq else None,
            "min": cpu_freq.min if cpu_freq and cpu_freq.min else None,
            "max": cpu_freq.max if cpu_freq and cpu_freq.max else None
        },
        "load_average": {
            "1min": load_avg[0],
            "5min": load_avg[1],
            "15min": load_avg[2]
        },
        "model": cpu_model
    }

def get_memory_info():
    """ดึงข้อมูล Memory"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "ram": {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    }

def get_disk_info():
    """ดึงข้อมูล Disk"""
    partitions = []
    
    for part in psutil.disk_partitions(all=False):
        if os.path.exists(part.mountpoint):
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
    
    # รวมข้อมูล I/O
    try:
        io_counters = psutil.disk_io_counters()
        io = {
            "read_count": io_counters.read_count,
            "write_count": io_counters.write_count,
            "read_bytes": io_counters.read_bytes,
            "write_bytes": io_counters.write_bytes,
            "read_time": io_counters.read_time,
            "write_time": io_counters.write_time
        }
    except:
        io = None
    
    return {
        "partitions": partitions,
        "io": io
    }

def get_network_info():
    """ดึงข้อมูล Network"""
    interfaces = {}
    
    # รวมข้อมูล interface
    net_if_addrs = psutil.net_if_addrs()
    for interface_name, addr_list in net_if_addrs.items():
        addresses = []
        for addr in addr_list:
            address_info = {
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast
            }
            addresses.append(address_info)
        
        interfaces[interface_name] = {
            "addresses": addresses
        }
    
    # รวมข้อมูล IO
    try:
        net_io_counters = psutil.net_io_counters(pernic=True)
        for interface_name, counters in net_io_counters.items():
            if interface_name in interfaces:
                interfaces[interface_name]["io"] = {
                    "bytes_sent": counters.bytes_sent,
                    "bytes_recv": counters.bytes_recv,
                    "packets_sent": counters.packets_sent,
                    "packets_recv": counters.packets_recv,
                    "errin": counters.errin,
                    "errout": counters.errout,
                    "dropin": counters.dropin,
                    "dropout": counters.dropout
                }
    except:
        pass
    
    # ดึงข้อมูล connections
    try:
        connections = psutil.net_connections(kind='inet')
        conn_stats = {
            "established": 0,
            "listen": 0,
            "time_wait": 0,
            "close_wait": 0,
            "other": 0
        }
        
        for conn in connections:
            status = conn.status.lower()
            if status == 'established':
                conn_stats["established"] += 1
            elif status == 'listen':
                conn_stats["listen"] += 1
            elif status == 'time_wait':
                conn_stats["time_wait"] += 1
            elif status == 'close_wait':
                conn_stats["close_wait"] += 1
            else:
                conn_stats["other"] += 1
    except:
        conn_stats = None
    
    return {
        "interfaces": interfaces,
        "connections": conn_stats
    }

def get_temperature_info():
    """ดึงข้อมูลอุณหภูมิ"""
    temps = {}
    
    try:
        # ดึงข้อมูลอุณหภูมิจาก psutil
        temps_psutil = psutil.sensors_temperatures()
        for chip, sensors in temps_psutil.items():
            temps[chip] = []
            for sensor in sensors:
                temps[chip].append({
                    "label": sensor.label,
                    "current": sensor.current,
                    "high": sensor.high,
                    "critical": sensor.critical
                })
    except:
        try:
            # ถ้า psutil ไม่ทำงาน ลองใช้ lm-sensors
            sensors_output = subprocess.check_output(['sensors', '-j'], text=True)
            temps = json.loads(sensors_output)
        except:
            temps = {"error": "ไม่สามารถดึงข้อมูลอุณหภูมิได้"}
    
    return temps

def get_uptime():
    """ดึงข้อมูล uptime"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        
        return {
            "seconds": uptime_seconds,
            "formatted": format_uptime(uptime_seconds)
        }
    except:
        return {
            "seconds": 0,
            "formatted": "Unknown"
        }

def format_uptime(seconds):
    """แปลง uptime เป็น human-readable format"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{int(days)} วัน, {int(hours)} ชั่วโมง, {int(minutes)} นาที"
    elif hours > 0:
        return f"{int(hours)} ชั่วโมง, {int(minutes)} นาที"
    else:
        return f"{int(minutes)} นาที, {int(seconds)} วินาที"

def store_in_influxdb(data):
    """เก็บข้อมูลลง InfluxDB"""
    timestamp = datetime.utcnow()
    
    # CPU metrics
    cpu_point = Point("cpu_metrics") \
        .tag("host", platform.node()) \
        .field("cpu_percent", data["cpu"]["percent"]) \
        .field("load_avg_1m", data["cpu"]["load_average"]["1min"]) \
        .field("load_avg_5m", data["cpu"]["load_average"]["5min"]) \
        .field("load_avg_15m", data["cpu"]["load_average"]["15min"]) \
        .time(timestamp)
    
    # Memory metrics
    mem_point = Point("memory_metrics") \
        .tag("host", platform.node()) \
        .field("memory_percent", data["memory"]["ram"]["percent"]) \
        .field("swap_percent", data["memory"]["swap"]["percent"]) \
        .time(timestamp)
    
    # Disk metrics for each partition
    for partition in data["disk"]["partitions"]:
        disk_point = Point("disk_metrics") \
            .tag("host", platform.node()) \
            .tag("mountpoint", partition["mountpoint"]) \
            .field("disk_percent", partition["percent"]) \
            .time(timestamp)
        
        write_api.write(
            bucket=settings["influxdb"]["bucket"],
            org=settings["influxdb"]["org"],
            record=disk_point
        )
    
    # Network metrics for each interface
    for interface_name, interface_data in data["network"]["interfaces"].items():
        if "io" in interface_data:
            net_point = Point("network_metrics") \
                .tag("host", platform.node()) \
                .tag("interface", interface_name) \
                .field("bytes_sent", interface_data["io"]["bytes_sent"]) \
                .field("bytes_recv", interface_data["io"]["bytes_recv"]) \
                .time(timestamp)
            
            write_api.write(
                bucket=settings["influxdb"]["bucket"],
                org=settings["influxdb"]["org"],
                record=net_point
            )
    
    # เขียนข้อมูล CPU และ Memory
    write_api.write(
        bucket=settings["influxdb"]["bucket"],
        org=settings["influxdb"]["org"],
        record=[cpu_point, mem_point]
    )

def check_thresholds(data):
    """ตรวจสอบค่า thresholds และส่งการแจ้งเตือนถ้าจำเป็น"""
    alerts = []
    
    # ตรวจสอบ CPU
    if data["cpu"]["percent"] > thresholds["cpu_percent"]:
        alerts.append(f"⚠️ CPU usage is high: {data['cpu']['percent']}% (threshold: {thresholds['cpu_percent']}%)")
    
    # ตรวจสอบ Memory
    if data["memory"]["ram"]["percent"] > thresholds["memory_percent"]:
        alerts.append(f"⚠️ Memory usage is high: {data['memory']['ram']['percent']}% (threshold: {thresholds['memory_percent']}%)")
    
    # ตรวจสอบ Disk
    for partition in data["disk"]["partitions"]:
        if partition["percent"] > thresholds["disk_percent"]:
            alerts.append(f"⚠️ Disk usage is high on {partition['mountpoint']}: {partition['percent']}% (threshold: {thresholds['disk_percent']}%)")
    
    # ตรวจสอบอุณหภูมิ (ถ้ามีข้อมูล)
    if isinstance(data["temperature"], dict) and "error" not in data["temperature"]:
        for chip, sensors in data["temperature"].items():
            if isinstance(sensors, list):
                for sensor in sensors:
                    if sensor.get("current") and sensor["current"] > thresholds["temperature"]:
                        alerts.append(f"⚠️ Temperature is high on {chip} {sensor.get('label', '')}: {sensor['current']}°C (threshold: {thresholds['temperature']}°C)")
    
    # ส่งการแจ้งเตือนถ้าจำเป็น
    if alerts and settings["discord"]["webhook_url"]:
        send_discord_alert(alerts, data)

def send_discord_alert(alerts, data):
    """ส่งการแจ้งเตือนไปยัง Discord"""
    webhook_url = settings["discord"]["webhook_url"]
    
    # สร้าง embed สำหรับ Discord
    embeds = [{
        "title": "🚨 System Alert",
        "description": "\n".join(alerts),
        "color": 16711680,  # สีแดง
        "fields": [
            {
                "name": "CPU Usage",
                "value": f"{data['cpu']['percent']}%",
                "inline": True
            },
            {
                "name": "Memory Usage",
                "value": f"{data['memory']['ram']['percent']}%",
                "inline": True
            },
            {
                "name": "System Uptime",
                "value": data["system"]["uptime"]["formatted"],
                "inline": True
            }
        ],
        "footer": {
            "text": f"Host: {data['system']['hostname']} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }]
    
    payload = {
        "content": "⚠️ **Alert Notification** ⚠️",
        "embeds": embeds
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        logging.info(f"Discord notification sent successfully: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send Discord notification: {str(e)}")

if __name__ == '__main__':
    # สร้าง config directory ถ้ายังไม่มี
    for directory in ['config', 'logs', 'prompts']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # สร้างไฟล์ settings.json ถ้ายังไม่มี
    if not os.path.exists('config/settings.json'):
        with open('config/settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    # สร้างไฟล์ thresholds.json ถ้ายังไม่มี
    if not os.path.exists('config/thresholds.json'):
        with open('config/thresholds.json', 'w') as f:
            json.dump(thresholds, f, indent=2)
    
    # สร้างไฟล์ system_summary_prompt.txt ถ้ายังไม่มี
    if not os.path.exists('prompts/system_summary_prompt.txt'):
        if not os.path.exists('prompts'):
            os.makedirs('prompts')
        with open('prompts/system_summary_prompt.txt', 'w') as f:
            f.write(system_summary_prompt)
    
    print("Starting Ubuntu Health Monitor API...")
    app.run(host='0.0.0.0', port=5000, debug=False)
