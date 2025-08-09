# 🖥️ Ubuntu Health Monitor

ระบบตรวจสอบและรายงานสถานะเซิร์ฟเวอร์ Ubuntu ที่ส่งการแจ้งเตือนผ่าน Discord โดยใช้ AI ช่วยแปลงข้อมูลทางเทคนิคให้เป็นภาษาไทยที่เข้าใจง่าย พร้อมแสดงผลแบบ Real-time ผ่าน Grafana Dashboard

## 📋 Project Stack

โปรเจกต์นี้ประกอบด้วยเทคโนโลยีดังนี้:

1. **ส่วนแสดงผล (Presentation Layer)**:
   - Discord: สำหรับรับการแจ้งเตือนที่สรุปมาอย่างสวยงาม อ่านง่าย และเข้าถึงได้จากทุกที่
   - Grafana: สำหรับแสดงผล Dashboard ข้อมูลแบบ Real-time และดูประวัติย้อนหลัง

2. **ส่วนควบคุมและทำงานอัตโนมัติ (Orchestration Layer)**: n8n (via Docker)
   - บทบาท: เป็นหัวใจของโปรเจกต์ ทำหน้าที่เป็น "ผู้ควบคุมวง" ที่คอยสั่งการทุกอย่างตามเวลาที่กำหนด (Schedule), เรียกใช้ API, ส่งข้อมูลไปให้ AI และส่งผลลัพธ์สุดท้ายไปที่ Discord

3. **ส่วนประมวลผลอัจฉริยะ (Intelligence Layer)**: OpenAI (ChatGPT API)
   - บทบาท: รับข้อมูลดิบ (JSON) เกี่ยวกับสถานะเซิร์ฟเวอร์มาแปลงเป็นข้อความภาษาไทยที่มนุษย์อ่านแล้วเข้าใจง่าย พร้อมช่วยวิเคราะห์และแจ้งเตือนจุดที่น่ากังวล

4. **ส่วนเก็บข้อมูล (Storage Layer)**: InfluxDB
   - บทบาท: เก็บข้อมูลประวัติการทำงานของระบบในรูปแบบ Time Series Database เพื่อใช้ในการแสดงผลและวิเคราะห์แนวโน้ม

5. **ส่วนหลังบ้านและ API (Backend/API Layer)**: Python + Flask
   - บทบาท: ทำหน้าที่เป็น API ขนาดเล็ก (Micro API) ที่ทำงานอยู่บนเครื่อง Ubuntu คอยรับคำสั่งจาก n8n แล้วส่งข้อมูลสถานะของเซิร์ฟเวอร์กลับไปในรูปแบบ JSON

6. **ส่วนดึงข้อมูล (Data Source Layer)**: Ubuntu 24 + Python Library psutil
   - บทบาท: เป็นต้นทางของข้อมูลทั้งหมด psutil คือเครื่องมือหลักที่สคริปต์ Python ใช้ในการเข้าไปอ่านค่า CPU, RAM, Disk และข้อมูลอื่นๆ ของระบบปฏิบัติการ Ubuntu

## 📂 โครงสร้างโปรเจกต์

```
Ubuntu-Health-Monitor/
├── app.py                            # Flask API หลัก
├── requirements.txt                  # รายการ package ที่ต้องใช้
├── docker-compose.yml                # สำหรับรัน n8n, InfluxDB และ Grafana
├── prompts/                          # โฟลเดอร์เก็บ prompts สำหรับ AI
│   └── system_summary_prompt.txt     # Prompt template สำหรับ OpenAI
├── workflows/                        # โฟลเดอร์เก็บ workflow ของ n8n
│   └── server_monitor_workflow.json  # n8n workflow หลัก
├── dashboards/                       # โฟลเดอร์เก็บ Grafana dashboards
│   └── system_overview.json          # Dashboard แสดงภาพรวมระบบ
├── scripts/                          # โฟลเดอร์เก็บสคริปต์ต่างๆ
│   ├── install.sh                    # สคริปต์ติดตั้งระบบ
│   ├── install_grafana_influxdb.sh   # สคริปต์ติดตั้ง Grafana และ InfluxDB
│   └── test_api.py                   # สคริปต์ทดสอบ API
├── logs/                             # โฟลเดอร์เก็บ log ต่างๆ
│   ├── api.log                       # Log ของ Flask API
│   └── system_data.log               # Log ข้อมูลระบบย้อนหลัง
├── config/                           # โฟลเดอร์เก็บไฟล์ตั้งค่า
│   ├── settings.json                 # การตั้งค่าทั่วไป
│   └── thresholds.json               # ค่าขีดจำกัดสำหรับการแจ้งเตือน
├── utils/                            # โฟลเดอร์เก็บโค้ดสนับสนุน
│   ├── data_processor.py             # โค้ดประมวลผลข้อมูล
│   └── discord_formatter.py          # โค้ดจัดรูปแบบข้อความสำหรับ Discord
├── systemd/                          # ไฟล์สำหรับตั้งค่า systemd service
│   └── ubuntu-health-monitor.service # systemd service file
├── docs/                             # เอกสารประกอบโปรเจกต์
│   ├── installation.md               # คู่มือการติดตั้ง
│   ├── configuration.md              # คู่มือการตั้งค่า
│   └── troubleshooting.md            # วิธีแก้ไขปัญหาที่พบบ่อย
├── tests/                            # โฟลเดอร์เก็บไฟล์ทดสอบ
│   ├── test_api.py                   # ไฟล์ทดสอบ API
│   └── test_system_info.py           # ไฟล์ทดสอบการดึงข้อมูลระบบ
├── influxdb-data/                    # โฟลเดอร์เก็บข้อมูล InfluxDB
├── grafana-data/                     # โฟลเดอร์เก็บข้อมูล Grafana
├── n8n-data/                         # โฟลเดอร์เก็บข้อมูล n8n
├── .gitignore                        # ไฟล์สำหรับกำหนดไฟล์ที่ไม่ต้องการใส่ใน Git
├── LICENSE                           # ไฟล์สัญญาอนุญาต MIT
└── README.md                         # คำอธิบายโปรเจกต์
```

## 🚀 การติดตั้ง

### 1. Clone โปรเจกต์และติดตั้ง Dependencies

```bash
# Clone โปรเจกต์
git clone https://github.com/diswarin/Ubuntu-Health-Monitor.git
cd Ubuntu-Health-Monitor

# สร้าง Virtual Environment
python -m venv venv
source venv/bin/activate  # สำหรับ Linux/Mac
# หรือ venv\Scripts\activate  # สำหรับ Windows

# ติดตั้ง Dependencies
pip install -r requirements.txt
```

### 2. การติดตั้ง Docker, Grafana และ InfluxDB

```bash
# ทำให้สคริปต์ติดตั้งสามารถทำงานได้
chmod +x scripts/install_grafana_influxdb.sh

# รันสคริปต์ติดตั้ง (ต้องใช้สิทธิ์ root)
sudo scripts/install_grafana_influxdb.sh
```

### 3. การตั้งค่า Discord Webhook

1. ไปที่ Discord Server ของคุณ
2. เลือก Channel ที่ต้องการรับการแจ้งเตือน
3. เข้าไปที่ Channel Settings > Integrations > Webhooks
4. สร้าง Webhook ใหม่และคัดลอก URL
5. นำ URL ไปใส่ในไฟล์ `config/settings.json`

### 4. การตั้งค่า OpenAI API

1. สร้าง API Key จาก [OpenAI Platform](https://platform.openai.com/)
2. นำ API Key ไปใส่ในการตั้งค่า n8n workflow

### 5. การตั้งค่า n8n Workflow

1. เปิด n8n ที่ http://localhost:5678/
2. นำเข้า workflow จากไฟล์ `workflows/server_monitor_workflow.json`
3. แก้ไขการตั้งค่าต่างๆ ให้ถูกต้อง:
   - IP Address ของ Ubuntu Server
   - Discord Webhook URL
   - OpenAI API Key
4. เปิดใช้งาน Workflow

### 6. การตั้งค่า Grafana Dashboard

1. เปิด Grafana ที่ http://localhost:3000/
2. เข้าสู่ระบบด้วย username และ password เริ่มต้น (admin/YourSecurePassword123)
3. ไปที่ Configuration > Data Sources > Add data source
4. เลือก InfluxDB และตั้งค่าดังนี้:
   - URL: http://influxdb:8086
   - Organization: ubuntu-monitor
   - Token: YourSecureToken123
   - Default Bucket: system-metrics
5. บันทึกและทดสอบการเชื่อมต่อ
6. ไปที่ Create > Import
7. อัปโหลดไฟล์ `dashboards/system_overview.json`

## 📊 การใช้งาน

เมื่อตั้งค่าเสร็จสิ้น ระบบจะทำงานดังนี้:

1. Flask API เก็บข้อมูลระบบและส่งไปยัง InfluxDB ทุกๆ 1 นาที
2. n8n จะเรียกข้อมูลจาก Flask API ทุก 30 นาที และส่งไปให้ OpenAI API
3. OpenAI API แปลงข้อมูลเป็นข้อความภาษาไทยที่เข้าใจง่าย
4. ผลลัพธ์จะถูกส่งไปยัง Discord channel ที่กำหนดไว้
5. Grafana แสดงผล Dashboard แบบ Real-time จากข้อมูลใน InfluxDB

## 🔄 ภาพรวมการทำงาน (Workflow Overview)

เพื่อให้เห็นภาพชัดขึ้น การทำงานของ Stack นี้จะเป็นไปตามลำดับนี้:

🔄 Flask API ดึงข้อมูลระบบและส่งเข้า InfluxDB ทุกๆ 1 นาที  
📊 Grafana แสดงผลข้อมูลจาก InfluxDB แบบ Real-time  
⏰ n8n เริ่มทำงานตามตารางเวลาที่ตั้งไว้ (ทุก 30 นาที)  
➡️ n8n ยิง HTTP Request ไปที่ Flask API  
⚙️ Flask API ส่งข้อมูลสถานะล่าสุดในรูปแบบ JSON  
🧠 n8n ส่งข้อมูล JSON ไปให้ OpenAI API พร้อมคำสั่งให้ช่วยสรุปเป็นภาษาไทย  
✍️ OpenAI ประมวลผลและส่งข้อความสรุปกลับมาให้ n8n  
💬 n8n นำข้อความที่ได้ มาจัดรูปแบบแล้วส่งเป็นการแจ้งเตือนเข้าไปใน Discord  

## 🔧 การปรับแต่ง

- ปรับเปลี่ยนความถี่ในการเก็บข้อมูลได้ที่ `config/settings.json`
- แก้ไข prompt ของ OpenAI ได้ที่ไฟล์ `prompts/system_summary_prompt.txt`
- ปรับแต่ง Grafana Dashboard ได้ตามต้องการ
- เพิ่มหรือลดข้อมูลที่ต้องการเก็บได้ที่ Flask API
- ปรับแต่งค่าขีดจำกัดสำหรับการแจ้งเตือนได้ที่ `config/thresholds.json`

## 📝 สิ่งที่ต้องทำเพิ่มเติม

- [ ] เพิ่มการตั้งค่าการแจ้งเตือน (Alerts) ใน Grafana
- [ ] เพิ่มการเก็บข้อมูลเพิ่มเติม เช่น Network I/O, Temperature
- [ ] สร้าง API endpoints เพิ่มเติมสำหรับการจัดการระบบ
- [ ] เพิ่มการตรวจสอบบริการ (Services) ที่ทำงานอยู่
- [ ] เพิ่มการตรวจสอบ Log Files เพื่อค้นหาข้อผิดพลาด
- [ ] สร้างระบบ Backup ข้อมูลสำคัญอัตโนมัติ

## 💡 เครดิต

พัฒนาโดย [diswarin](https://github.com/diswarin) เมื่อ สิงหาคม 2025

## 📄 License

[MIT License](LICENSE)
