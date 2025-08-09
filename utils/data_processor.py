#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu Health Monitor - Data Processor

ใช้สำหรับประมวลผลข้อมูลระบบ
"""

import json
import logging
import time
from datetime import datetime, timedelta
import statistics

class DataProcessor:
    """
    คลาสสำหรับประมวลผลข้อมูลระบบ
    """
    
    def __init__(self, data_file='logs/system_data.log', max_entries=1000):
        """
        กำหนดค่าเริ่มต้นสำหรับ Data Processor
        
        Args:
            data_file (str): ไฟล์ที่จะใช้เก็บข้อมูลระบบ
            max_entries (int): จำนวนข้อมูลสูงสุดที่จะเก็บไว้
        """
        self.data_file = data_file
        self.max_entries = max_entries
        self.data = []
        self.load_data()
    
    def load_data(self):
        """โหลดข้อมูลจากไฟล์"""
        try:
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
                # โหลดเฉพาะข้อมูลล่าสุดตามจำนวนที่กำหนด
                for line in lines[-self.max_entries:]:
                    try:
                        entry = json.loads(line.strip())
                        self.data.append(entry)
                    except json.JSONDecodeError:
                        logging.warning(f"ไม่สามารถ parse ข้อมูล: {line}")
                        continue
        except FileNotFoundError:
            logging.info(f"ไม่พบไฟล์ {self.data_file} สร้างไฟล์ใหม่")
    
    def save_data(self, system_data):
        """
        บันทึกข้อมูลระบบลงในไฟล์
        
        Args:
            system_data (dict): ข้อมูลระบบที่จะบันทึก
        """
        # เพิ่ม timestamp
        system_data['timestamp'] = datetime.now().isoformat()
        
        # เพิ่มข้อมูลลงใน list
        self.data.append(system_data)
        
        # ตัดข้อมูลเก่าออกถ้ามีมากเกินไป
        if len(self.data) > self.max_entries:
            self.data = self.data[-self.max_entries:]
        
        # บันทึกข้อมูลลงไฟล์
        try:
            with open(self.data_file, 'a') as f:
                f.write(json.dumps(system_data) + '\n')
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกข้อมูลลงไฟล์: {str(e)}")
    
    def get_average(self, hours=24, metric='cpu'):
        """
        คำนวณค่าเฉลี่ยของเมตริกที่ระบุในช่วงเวลาที่กำหนด
        
        Args:
            hours (int): จำนวนชั่วโมงย้อนหลังที่จะคำนวณ
            metric (str): เมตริกที่จะคำนวณ ('cpu', 'memory', 'disk')
            
        Returns:
            float: ค่าเฉลี่ยของเมตริก
        """
        if not self.data:
            return None
        
        # กำหนดเวลาเริ่มต้น
        start_time = datetime.now() - timedelta(hours=hours)
        
        # กรองข้อมูลตามช่วงเวลา
        filtered_data = []
        for entry in self.data:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time >= start_time:
                    if metric == 'cpu' and 'cpu' in entry:
                        filtered_data.append(entry['cpu']['percent'])
                    elif metric == 'memory' and 'memory' in entry:
                        filtered_data.append(entry['memory']['ram']['percent'])
                    elif metric == 'disk' and 'disk' in entry:
                        # ใช้พาร์ติชันแรกเป็นตัวแทน
                        if entry['disk']['partitions']:
                            filtered_data.append(entry['disk']['partitions'][0]['percent'])
            except (KeyError, ValueError) as e:
                logging.warning(f"ข้อมูลไม่ถูกต้อง: {str(e)}")
                continue
        
        # คำนวณค่าเฉลี่ย
        if filtered_data:
            return statistics.mean(filtered_data)
        else:
            return None
    
    def detect_anomalies(self, threshold_multiplier=1.5):
        """
        ตรวจหาค่าผิดปกติในข้อมูลโดยใช้ IQR (Interquartile Range)
        
        Args:
            threshold_multiplier (float): ตัวคูณสำหรับ IQR เพื่อกำหนดขอบเขต
            
        Returns:
            dict: รายการค่าผิดปกติแยกตามเมตริก
        """
        if len(self.data) < 10:
            return {"error": "ข้อมูลไม่เพียงพอสำหรับการวิเคราะห์"}
        
        # เตรียมข้อมูลสำหรับวิเคราะห์
        cpu_data = []
        memory_data = []
        disk_data = []
        
        for entry in self.data:
            try:
                if 'cpu' in entry:
                    cpu_data.append(entry['cpu']['percent'])
                if 'memory' in entry:
                    memory_data.append(entry['memory']['ram']['percent'])
                if 'disk' in entry and entry['disk']['partitions']:
                    disk_data.append(entry['disk']['partitions'][0]['percent'])
            except KeyError:
                continue
        
        # ฟังก์ชันสำหรับคำนวณค่าผิดปกติ
        def find_anomalies(data):
            if len(data) < 10:
                return []
            
            # คำนวณ quartiles
            sorted_data = sorted(data)
            q1 = sorted_data[len(sorted_data) // 4]
            q3 = sorted_data[3 * len(sorted_data) // 4]
            iqr = q3 - q1
            
            # กำหนดขอบเขต
            lower_bound = q1 - threshold_multiplier * iqr
            upper_bound = q3 + threshold_multiplier * iqr
            
            # ค้นหาค่าผิดปกติ
            anomalies = [x for x in data if x < lower_bound or x > upper_bound]
            return anomalies
        
        # ค้นหาค่าผิดปกติสำหรับแต่ละเมตริก
        return {
            "cpu": find_anomalies(cpu_data),
            "memory": find_anomalies(memory_data),
            "disk": find_anomalies(disk_data)
        }
    
    def predict_usage_trend(self, days=7, metric='cpu'):
        """
        ทำนายแนวโน้มการใช้งานในอนาคต
        
        Args:
            days (int): จำนวนวันที่จะทำนาย
            metric (str): เมตริกที่จะทำนาย ('cpu', 'memory', 'disk')
            
        Returns:
            dict: ข้อมูลแนวโน้มการใช้งาน
        """
        if len(self.data) < 2:
            return {"error": "ข้อมูลไม่เพียงพอสำหรับการทำนาย"}
        
        # เตรียมข้อมูลสำหรับวิเคราะห์
        timestamps = []
        values = []
        
        for entry in self.data:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                timestamps.append(timestamp.timestamp())
                
                if metric == 'cpu' and 'cpu' in entry:
                    values.append(entry['cpu']['percent'])
                elif metric == 'memory' and 'memory' in entry:
                    values.append(entry['memory']['ram']['percent'])
                elif metric == 'disk' and 'disk' in entry and entry['disk']['partitions']:
                    values.append(entry['disk']['partitions'][0]['percent'])
                else:
                    continue
            except (KeyError, ValueError):
                continue
        
        if len(timestamps) < 2:
            return {"error": "ข้อมูลไม่เพียงพอสำหรับการทำนาย"}
        
        # คำนวณแนวโน้มอย่างง่าย (linear regression)
        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_xx = sum(x * x for x in timestamps)
        
        # คำนวณค่า slope และ intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # ทำนายค่าในอนาคต
        future_predictions = []
        last_timestamp = timestamps[-1]
        
        for i in range(1, days + 1):
            future_time = last_timestamp + i * 86400  # เพิ่มทีละวัน (86400 วินาที)
            prediction = slope * future_time + intercept
            
            # ปรับค่าให้อยู่ในช่วง 0-100
            prediction = max(0, min(100, prediction))
            
            future_date = datetime.fromtimestamp(future_time).strftime('%Y-%m-%d')
            future_predictions.append({
                "date": future_date,
                "prediction": round(prediction, 2)
            })
        
        # คำนวณความแม่นยำของโมเดล (R-squared)
        mean_y = sum_y / n
        ss_total = sum((y - mean_y) ** 2 for y in values)
        ss_residual = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(timestamps, values))
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        return {
            "metric": metric,
            "current_value": values[-1] if values else None,
            "trend": "increasing" if slope > 0.0001 else "decreasing" if slope < -0.0001 else "stable",
            "slope": slope,
            "r_squared": r_squared,
            "predictions": future_predictions
        }
    
    def get_peak_usage_times(self, metric='cpu'):
        """
        ค้นหาช่วงเวลาที่มีการใช้งานสูงสุด
        
        Args:
            metric (str): เมตริกที่จะวิเคราะห์ ('cpu', 'memory', 'disk')
            
        Returns:
            dict: ข้อมูลช่วงเวลาที่มีการใช้งานสูงสุด
        """
        if not self.data:
            return {"error": "ไม่มีข้อมูลสำหรับการวิเคราะห์"}
        
        # เตรียมข้อมูลตามช่วงเวลา
        hourly_data = {i: [] for i in range(24)}  # 0-23 ชั่วโมง
        
        for entry in self.data:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                hour = timestamp.hour
                
                if metric == 'cpu' and 'cpu' in entry:
                    hourly_data[hour].append(entry['cpu']['percent'])
                elif metric == 'memory' and 'memory' in entry:
                    hourly_data[hour].append(entry['memory']['ram']['percent'])
                elif metric == 'disk' and 'disk' in entry and entry['disk']['partitions']:
                    hourly_data[hour].append(entry['disk']['partitions'][0]['percent'])
            except (KeyError, ValueError):
                continue
        
        # คำนวณค่าเฉลี่ยของแต่ละช่วงเวลา
        hourly_averages = {}
        for hour, values in hourly_data.items():
            if values:
                hourly_averages[hour] = sum(values) / len(values)
        
        # เรียงลำดับตามค่าเฉลี่ยจากมากไปน้อย
        sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
        
        # สร้างผลลัพธ์
        peak_hours = [{"hour": hour, "average": round(avg, 2)} for hour, avg in sorted_hours[:5]]
        
        return {
            "metric": metric,
            "peak_hours": peak_hours,
            "lowest_hour": {"hour": sorted_hours[-1][0], "average": round(sorted_hours[-1][1], 2)} if sorted_hours else None
        }

if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    processor = DataProcessor()
    
    # สร้างข้อมูลทดสอบ
    import random
    from datetime import datetime, timedelta
    
    # สร้างข้อมูลจำลองย้อนหลัง 7 วัน
    start_date = datetime.now() - timedelta(days=7)
    for i in range(7 * 24):  # ทุกชั่วโมงเป็นเวลา 7 วัน
        test_date = start_date + timedelta(hours=i)
        test_data = {
            "cpu": {
                "percent": random.uniform(10, 90)
            },
            "memory": {
                "ram": {
                    "percent": random.uniform(20, 80)
                }
            },
            "disk": {
                "partitions": [
                    {
                        "percent": random.uniform(30, 70)
                    }
                ]
            },
            "timestamp": test_date.isoformat()
        }
        processor.save_data(test_data)
    
    # ทดสอบฟังก์ชันต่างๆ
    print("Average CPU (24h):", processor.get_average(hours=24, metric='cpu'))
    print("Anomalies:", processor.detect_anomalies())
    print("CPU Trend prediction:", processor.predict_usage_trend(days=3, metric='cpu'))
    print("Peak usage times:", processor.get_peak_usage_times(metric='cpu'))
