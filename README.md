# 🖥️ Ubuntu Health Monitor

ระบบตรวจสอบและรายงานสถานะเซิร์ฟเวอร์ Ubuntu ที่ส่งการแจ้งเตือนผ่าน Discord โดยใช้ AI ช่วยแปลงข้อมูลทางเทคนิคให้เป็นภาษาไทยที่เข้าใจง่าย

## 📋 Project Stack

โปรเจกต์นี้ประกอบด้วยเทคโนโลยีดังนี้:

1. **ส่วนแสดงผล (Presentation Layer)**: Discord
2. **ส่วนควบคุมและทำงานอัตโนมัติ (Orchestration Layer)**: n8n (via Docker)
3. **ส่วนประมวลผลอัจฉริยะ (Intelligence Layer)**: OpenAI (ChatGPT API)
4. **ส่วนหลังบ้านและ API (Backend/API Layer)**: Python + Flask
5. **ส่วนดึงข้อมูล (Data Source Layer)**: Ubuntu 24 + Python Library psutil


Ubuntu-Health-Monitor/
├── app.py                         # Flask API หลัก
├── requirements.txt               # รายการ package ที่ต้องใช้
├── docker-compose.yml             # สำหรับรัน n8n
├── prompts/
│   └── system_summary_prompt.txt  # Prompt template สำหรับ OpenAI
├── workflows/
│   └── server_monitor_workflow.json  # n8n workflow
├── ubuntu-health-monitor.service  # systemd service file
├── test_api.py                    # ไฟล์ทดสอบ API
└── README.md                      # คำอธิบายโปรเจกต์

## 🚀 การติดตั้ง

### 1. การติดตั้ง Flask API

```bash
# สร้าง Virtual Environment
python -m venv venv
source venv/bin/activate  # สำหรับ Linux/Mac
# หรือ venv\Scripts\activate  # สำหรับ Windows

# ติดตั้ง Dependencies
pip install -r requirements.txt

# รัน Flask API
python app.py
```

### 2. การติดตั้ง n8n ด้วย Docker

```bash
# แก้ไขค่าใน docker-compose.yml ให้เหมาะสม
# รัน Docker Compose
docker-compose up -d
```

### 3. การตั้งค่า Discord Webhook

1. ไปที่ Discord Server ของคุณ
2. เลือก Channel ที่ต้องการรับการแจ้งเตือน
3. เข้าไปที่ Channel Settings > Integrations > Webhooks
4. สร้าง Webhook ใหม่และคัดลอก URL
5. นำ URL ไปใส่ในการตั้งค่า n8n workflow

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

## 📊 การใช้งาน

เมื่อตั้งค่าเสร็จสิ้น ระบบจะทำงานตามกำหนดเวลาดังนี้:

1. n8n จะเรียกข้อมูลจาก Flask API ทุก 30 นาที
2. ข้อมูลจะถูกส่งไปให้ OpenAI API เพื่อแปลงเป็นข้อความภาษาไทยที่เข้าใจง่าย
3. ผลลัพธ์จะถูกส่งไปยัง Discord channel ที่กำหนดไว้

## 🔧 การปรับแต่ง

- ปรับเปลี่ยนความถี่ในการตรวจสอบได้ที่ n8n workflow
- แก้ไข prompt ของ OpenAI ได้ที่ไฟล์ `prompts/system_summary_prompt.txt`
- เพิ่มหรือลดข้อมูลที่ต้องการเก็บได้ที่ Flask API

## 📝 สิ่งที่ต้องทำเพิ่มเติม

- [ ] เพิ่มการเก็บข้อมูลย้อนหลังเพื่อดูแนวโน้ม
- [ ] เพิ่มการแจ้งเตือนเมื่อค่าเกินกำหนด
- [ ] สร้างหน้า Dashboard สำหรับดูข้อมูลแบบ Real-time

## 📄 License

[MIT License](LICENSE)
