# Ubuntu Health Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ระบบติดตามและวิเคราะห์สถานะเซิร์ฟเวอร์ Ubuntu แบบเรียลไทม์ ด้วยการผสมผสาน AI, Data Visualization และการแจ้งเตือนอัตโนมัติ

![System Overview](https://raw.githubusercontent.com/diswarin/Ubuntu-Health-Monitor/main/docs/system_overview.png)

## 📋 คุณสมบัติหลัก

- **ติดตามทรัพยากรระบบแบบเรียลไทม์** - CPU, RAM, Disk, Network, Temperature
- **AI-Powered Analysis** - วิเคราะห์ข้อมูลระบบด้วย OpenAI API
- **Interactive Dashboards** - Grafana dashboards สำหรับแสดงข้อมูลแบบ real-time
- **ระบบแจ้งเตือนอัตโนมัติ** - แจ้งเตือนผ่าน Discord เมื่อระบบมีปัญหา
- **Workflow Automation** - ใช้ n8n สำหรับการทำงานอัตโนมัติ
- **Time-Series Database** - จัดเก็บข้อมูลประวัติด้วย InfluxDB
- **RESTful API** - API สำหรับดึงข้อมูลระบบ

## 🛠️ Project Stack

- **Backend**: Python 3, Flask
- **Database**: InfluxDB
- **Visualization**: Grafana
- **Workflow Automation**: n8n
- **AI**: OpenAI API (GPT-4)
- **Containerization**: Docker, Docker Compose
- **Notification**: Discord Webhook

## 📁 โครงสร้างโปรเจค

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
├── .gitignore                        # ไฟล์สำหรับกำหนดไฟล์ที่ไม่ต้องการใส่ใน Git
├── LICENSE                           # ไฟล์สัญญาอนุญาต MIT
└── README.md                         # คำอธิบายโปรเจกต์
```

## 🔧 การติดตั้ง

### ติดตั้งแบบอัตโนมัติ

```bash
git clone https://github.com/diswarin/Ubuntu-Health-Monitor.git
cd Ubuntu-Health-Monitor
chmod +x scripts/install.sh
./scripts/install.sh
```

### ติดตั้งด้วยตนเอง

1. โคลนโปรเจค:
```bash
git clone https://github.com/diswarin/Ubuntu-Health-Monitor.git
cd Ubuntu-Health-Monitor
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

3. ตั้งค่า API key:
```bash
cp config/settings.json.example config/settings.json
# แก้ไขไฟล์ settings.json เพื่อใส่ API key และการตั้งค่าอื่นๆ
```

4. ตั้งค่า thresholds สำหรับการแจ้งเตือน:
```bash
cp config/thresholds.json.example config/thresholds.json
# แก้ไขไฟล์ thresholds.json ตามความต้องการ
```

5. รัน Docker containers สำหรับ InfluxDB, Grafana และ n8n:
```bash
docker-compose up -d
```

6. รัน Flask API:
```bash
python app.py
```

7. ตั้งค่า systemd service (ถ้าต้องการรันเป็น service):
```bash
sudo cp systemd/ubuntu-health-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ubuntu-health-monitor
sudo systemctl start ubuntu-health-monitor
```

## 🚀 การใช้งาน

### API Endpoints

- **GET /api/v1/system/info** - ข้อมูลระบบทั้งหมด
- **GET /api/v1/system/cpu** - ข้อมูล CPU
- **GET /api/v1/system/memory** - ข้อมูล Memory
- **GET /api/v1/system/disk** - ข้อมูล Disk
- **GET /api/v1/system/network** - ข้อมูล Network
- **GET /api/v1/system/temperature** - ข้อมูลอุณหภูมิ
- **GET /api/v1/system/summary** - สรุปสถานะระบบด้วย AI

### Grafana Dashboard

1. เข้าถึง Grafana dashboard ที่ http://localhost:3000
2. Login ด้วย Username: `admin` และ Password: `admin`
3. เลือก Dashboard "System Overview"

### n8n Workflow

1. เข้าถึง n8n dashboard ที่ http://localhost:5678
2. Import workflow จากไฟล์ `workflows/server_monitor_workflow.json`
3. ตั้งค่า credentials สำหรับ Discord webhook
4. เปิดใช้งาน workflow

## 📊 ภาพรวมการทำงาน

![Architecture](https://raw.githubusercontent.com/diswarin/Ubuntu-Health-Monitor/main/docs/images/architecture.png)

1. **Data Collection**: Flask API ทำหน้าที่เก็บข้อมูลระบบผ่าน psutil และ subprocess
2. **Data Storage**: ข้อมูลถูกส่งไปเก็บใน InfluxDB เพื่อใช้ในการแสดงผลและวิเคราะห์
3. **Data Visualization**: Grafana ดึงข้อมูลจาก InfluxDB มาแสดงผลในรูปแบบกราฟและแดชบอร์ด
4. **Workflow Automation**: n8n ทำหน้าที่ตรวจสอบข้อมูลและส่งการแจ้งเตือนเมื่อมีปัญหา
5. **AI Analysis**: ข้อมูลถูกส่งไปวิเคราะห์ด้วย OpenAI API เพื่อให้ AI ช่วยสรุปสถานะระบบ
6. **Alerting**: ระบบส่งการแจ้งเตือนผ่าน Discord webhook เมื่อพบปัญหาหรือเมื่อทรัพยากรระบบสูงเกินค่าที่กำหนด

## ⚙️ การปรับแต่ง

### การตั้งค่า Thresholds

แก้ไขไฟล์ `config/thresholds.json` เพื่อปรับค่า thresholds สำหรับการแจ้งเตือน:

```json
{
  "cpu_percent": 80,
  "memory_percent": 85,
  "disk_percent": 90,
  "temperature": 70
}
```

### การตั้งค่า OpenAI API

แก้ไขไฟล์ `config/settings.json` เพื่อตั้งค่า OpenAI API:

```json
{
  "openai": {
    "api_key": "your-api-key",
    "model": "gpt-4"
  },
  "discord": {
    "webhook_url": "your-discord-webhook-url"
  }
}
```

### การปรับแต่ง Prompts

แก้ไขไฟล์ `prompts/system_summary_prompt.txt` เพื่อปรับเปลี่ยน prompt ที่ส่งไปยัง OpenAI API

## 📝 TODO

- [ ] เพิ่มการรองรับระบบปฏิบัติการอื่นนอกเหนือจาก Ubuntu
- [ ] เพิ่มการรองรับการแจ้งเตือนผ่านช่องทางอื่น (Line, Telegram, Email)
- [ ] เพิ่ม machine learning สำหรับการทำนายปัญหาที่อาจเกิดขึ้น
- [ ] สร้างหน้า Web UI สำหรับการตั้งค่าระบบ
- [ ] เพิ่มความสามารถในการตรวจสอบและจัดการกระบวนการ (processes)
- [ ] เพิ่มการตรวจสอบความปลอดภัย
- [ ] สร้าง API endpoint สำหรับการตั้งค่าแบบ RESTful
- [ ] ปรับปรุงประสิทธิภาพของการเก็บข้อมูลและการวิเคราะห์

## 👨‍💻 การสนับสนุน

หากคุณพบปัญหาหรือมีคำแนะนำ โปรดเปิด issue ใน GitHub repository นี้

## 📄 ลิขสิทธิ์

โครงการนี้อยู่ภายใต้ลิขสิทธิ์ MIT - ดูรายละเอียดใน [LICENSE](LICENSE)

## 🙏 เครดิต

- [psutil](https://github.com/giampaolo/psutil) - Python system utilities
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [InfluxDB](https://www.influxdata.com/) - Time series database
- [Grafana](https://grafana.com/) - Data visualization platform
- [n8n](https://n8n.io/) - Workflow automation tool
- [OpenAI](https://openai.com/) - AI language model
