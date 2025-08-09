#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu Health Monitor - Discord Formatter

ใช้สำหรับจัดรูปแบบข้อความที่จะส่งไปยัง Discord
"""

import json
from datetime import datetime
import requests
import os
import logging

class DiscordFormatter:
    """
    คลาสสำหรับจัดรูปแบบและส่งข้อความไปยัง Discord
    """
    
    def __init__(self, webhook_url=None, settings_path="config/settings.json"):
        """
        กำหนดค่าเริ่มต้นสำหรับ Discord Formatter
        
        Args:
            webhook_url (str, optional): Discord webhook URL
            settings_path (str): ที่อยู่ของไฟล์ settings.json
        """
        self.webhook_url = webhook_url
        
        # ถ้าไม่ได้ระบุ webhook_url ให้โหลดจากไฟล์ settings.json
        if not webhook_url:
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    self.webhook_url = settings.get('discord', {}).get('webhook_url', '')
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.error(f"ไม่สามารถโหลดการตั้งค่า Discord: {str(e)}")
                self.webhook_url = ''
    
    def format_system_alert(self, alerts, system_data):
        """
        จัดรูปแบบข้อความแจ้งเตือนสำหรับปัญหาระบบ
        
        Args:
            alerts (list): รายการการแจ้งเตือน
            system_data (dict): ข้อมูลระบบ
            
        Returns:
            dict: payload สำหรับส่งไปยัง Discord webhook
        """
        embeds = [{
            "title": "🚨 System Alert",
            "description": "\n".join(alerts),
            "color": 16711680,  # สีแดง
            "fields": [
                {
                    "name": "CPU Usage",
                    "value": f"{system_data['cpu']['percent']}%",
                    "inline": True
                },
                {
                    "name": "Memory Usage",
                    "value": f"{system_data['memory']['ram']['percent']}%",
                    "inline": True
                },
                {
                    "name": "System Uptime",
                    "value": system_data['system']['uptime']['formatted'],
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Host: {system_data['system']['hostname']} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }]
        
        return {
            "content": "⚠️ **Alert Notification** ⚠️",
            "embeds": embeds
        }
    
    def format_system_report(self, system_data, ai_summary=None):
        """
        จัดรูปแบบรายงานสถานะระบบประจำวัน
        
        Args:
            system_data (dict): ข้อมูลระบบ
            ai_summary (str, optional): สรุปข้อมูลจาก AI
            
        Returns:
            dict: payload สำหรับส่งไปยัง Discord webhook
        """
        # คำนวณสถานะทั่วไปของระบบ
        cpu_status = "🟢 Good"
        if system_data['cpu']['percent'] > 80:
            cpu_status = "🔴 Critical"
        elif system_data['cpu']['percent'] > 60:
            cpu_status = "🟠 Warning"
        
        memory_status = "🟢 Good"
        if system_data['memory']['ram']['percent'] > 85:
            memory_status = "🔴 Critical"
        elif system_data['memory']['ram']['percent'] > 70:
            memory_status = "🟠 Warning"
        
        # หาพาร์ติชันที่มีพื้นที่เหลือน้อยที่สุด
        disk_status = "🟢 Good"
        lowest_free_partition = ""
        lowest_free_percent = 100
        
        for partition in system_data['disk']['partitions']:
            if partition['percent'] < lowest_free_percent:
                lowest_free_percent = partition['percent']
                lowest_free_partition = partition['mountpoint']
            
            if partition['percent'] > 90:
                disk_status = "🔴 Critical"
            elif partition['percent'] > 80 and disk_status != "🔴 Critical":
                disk_status = "🟠 Warning"
        
        # สร้าง embed สำหรับ Discord
        system_info_embed = {
            "title": "📊 System Status Report",
            "description": f"Daily status report for **{system_data['system']['hostname']}**",
            "color": 3447003,  # สีฟ้า
            "fields": [
                {
                    "name": "CPU",
                    "value": f"{cpu_status}\n{system_data['cpu']['percent']}% used\nLoad: {system_data['cpu']['load_average']['1min']:.2f}, {system_data['cpu']['load_average']['5min']:.2f}, {system_data['cpu']['load_average']['15min']:.2f}",
                    "inline": True
                },
                {
                    "name": "Memory",
                    "value": f"{memory_status}\n{system_data['memory']['ram']['percent']}% used\nSwap: {system_data['memory']['swap']['percent']}% used",
                    "inline": True
                },
                {
                    "name": "Disk",
                    "value": f"{disk_status}\n{lowest_free_partition}: {lowest_free_percent}% used",
                    "inline": True
                },
                {
                    "name": "System Info",
                    "value": f"Platform: {system_data['system']['platform']}\nKernel: {system_data['system']['kernel']}\nUptime: {system_data['system']['uptime']['formatted']}",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        embeds = [system_info_embed]
        
        # เพิ่ม AI summary ถ้ามี
        if ai_summary:
            ai_embed = {
                "title": "🤖 AI Analysis",
                "description": ai_summary[:4000] if len(ai_summary) > 4000 else ai_summary,  # จำกัดความยาวไม่เกิน 4000 ตัวอักษร
                "color": 10181046  # สีม่วง
            }
            embeds.append(ai_embed)
        
        return {
            "content": "📋 **Daily System Status Report**",
            "embeds": embeds
        }
    
    def format_critical_error(self, error_message, context=None):
        """
        จัดรูปแบบข้อความแจ้งเตือนสำหรับข้อผิดพลาดร้ายแรง
        
        Args:
            error_message (str): ข้อความแสดงข้อผิดพลาด
            context (dict, optional): ข้อมูลเพิ่มเติมเกี่ยวกับข้อผิดพลาด
            
        Returns:
            dict: payload สำหรับส่งไปยัง Discord webhook
        """
        embed = {
            "title": "💥 Critical Error",
            "description": error_message,
            "color": 15158332,  # สีแดงเข้ม
            "fields": []
        }
        
        if context:
            for key, value in context.items():
                # แปลงค่าเป็น string และจำกัดความยาว
                if isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value, indent=2)
                value_str = str(value)
                if len(value_str) > 1000:
                    value_str = value_str[:997] + "..."
                
                embed["fields"].append({
                    "name": key,
                    "value": f"```\n{value_str}\n```",
                    "inline": False
                })
        
        embed["footer"] = {
            "text": f"Error occurred at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        return {
            "content": "🚨 **CRITICAL ERROR** 🚨",
            "embeds": [embed]
        }
    
    def format_command_output(self, command, output, return_code=0):
        """
        จัดรูปแบบข้อความสำหรับผลลัพธ์ของคำสั่ง
        
        Args:
            command (str): คำสั่งที่ใช้
            output (str): ผลลัพธ์ของคำสั่ง
            return_code (int): รหัสส่งคืนของคำสั่ง
            
        Returns:
            dict: payload สำหรับส่งไปยัง Discord webhook
        """
        status = "✅ Success" if return_code == 0 else f"❌ Failed (code: {return_code})"
        
        # จำกัดความยาวของผลลัพธ์
        if len(output) > 4000:
            output = output[:3997] + "..."
        
        embed = {
            "title": "⌨️ Command Execution",
            "fields": [
                {
                    "name": "Command",
                    "value": f"```bash\n{command}\n```",
                    "inline": False
                },
                {
                    "name": f"Output ({status})",
                    "value": f"```\n{output}\n```",
                    "inline": False
                }
            ],
            "color": 3066993 if return_code == 0 else 15158332,  # สีเขียวถ้าสำเร็จ, สีแดงถ้าล้มเหลว
            "footer": {
                "text": f"Executed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        return {
            "embeds": [embed]
        }
    
    def send_message(self, payload):
        """
        ส่งข้อความไปยัง Discord webhook
        
        Args:
            payload (dict): ข้อมูลที่จะส่ง
            
        Returns:
            bool: True ถ้าส่งสำเร็จ, False ถ้าล้มเหลว
        """
        if not self.webhook_url:
            logging.error("ไม่ได้ตั้งค่า Discord webhook URL")
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"ไม่สามารถส่งข้อความไปยัง Discord: {str(e)}")
            return False

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # สร้างข้อมูลทดสอบ
    test_data = {
        "cpu": {
            "percent": 75,
            "load_average": {
                "1min": 2.5,
                "5min": 2.2,
                "15min": 1.8
            }
        },
        "memory": {
            "ram": {
                "percent": 65
            },
            "swap": {
                "percent": 10
            }
        },
        "disk": {
            "partitions": [
                {
                    "mountpoint": "/",
                    "percent": 45
                },
                {
                    "mountpoint": "/home",
                    "percent": 78
                }
            ]
        },
        "system": {
            "hostname": "test-server",
            "platform": "Linux-5.15.0-x86_64-with-glibc2.35",
            "kernel": "5.15.0",
            "uptime": {
                "formatted": "5 days, 3 hours, 42 minutes"
            }
        }
    }
    
    # ทดสอบการสร้าง payload สำหรับ webhook
    formatter = DiscordFormatter()
    
    # ทดสอบ system alert
    alerts = [
        "⚠️ CPU usage is high: 75% (threshold: 70%)",
        "⚠️ Disk usage is high on /home: 78% (threshold: 75%)"
    ]
    alert_payload = formatter.format_system_alert(alerts, test_data)
    print("System Alert Payload:")
    print(json.dumps(alert_payload, indent=2))
    
    # ทดสอบ system report
    ai_summary = "ระบบทำงานปกติ แต่การใช้งาน CPU อยู่ในระดับสูง และพื้นที่ /home เริ่มเต็ม แนะนำให้ล้างไฟล์ที่ไม่จำเป็น"
    report_payload = formatter.format_system_report(test_data, ai_summary)
    print("\nSystem Report Payload:")
    print(json.dumps(report_payload, indent=2))
    
    # ทดสอบ critical error
    error_payload = formatter.format_critical_error(
        "ไม่สามารถเชื่อมต่อกับ InfluxDB ได้",
        {"exception": "ConnectionRefusedError", "attempts": 3}
    )
    print("\nCritical Error Payload:")
    print(json.dumps(error_payload, indent=2))
    
    # ทดสอบ command output
    command_payload = formatter.format_command_output(
        "df -h",
        "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        50G   22G   28G  45% /\n/dev/sda2       200G  156G   44G  78% /home"
    )
    print("\nCommand Output Payload:")
    print(json.dumps(command_payload, indent=2))
    
    # ถ้ามีการตั้งค่า webhook URL ไว้ จะทดสอบการส่งข้อความ
    if formatter.webhook_url:
        print("\nทดสอบส่งข้อความไปยัง Discord...")
        success = formatter.send_message(report_payload)
        print(f"ผลลัพธ์: {'สำเร็จ' if success else 'ล้มเหลว'}")
