# คู่มือการติดตั้ง Ubuntu Health Monitor

คู่มือนี้จะแนะนำวิธีการติดตั้ง Ubuntu Health Monitor บน Ubuntu Server

## ความต้องการของระบบ

- Ubuntu 20.04 LTS หรือใหม่กว่า
- Python 3.8 หรือใหม่กว่า
- Docker และ Docker Compose
- พื้นที่ว่างอย่างน้อย 2GB
- หน่วยความจำอย่างน้อย 2GB RAM

## การติดตั้งแบบอัตโนมัติ

วิธีที่ง่ายที่สุดในการติดตั้ง Ubuntu Health Monitor คือใช้สคริปต์ติดตั้งอัตโนมัติที่เราจัดเตรียมไว้

1. โคลนโปรเจค:

```bash
git clone https://github.com/diswarin/Ubuntu-Health-Monitor.git
cd Ubuntu-Health-Monitor
```

2. ให้สิทธิในการเรียกใช้งานสคริปต์:

```bash
chmod +x scripts/install.sh
```

3. รันสคริปต์ติดตั้ง (จำเป็นต้องใช้สิทธิ์ root):

```bash
sudo ./scripts/install.sh
```

สคริปต์จะทำงานต่อไปนี้:
- ติดตั้ง dependencies ที่จำเป็น
- ตั้งค่า lm-sensors สำหรับการอ่านข้อมูลอุณหภูมิ
- ติดตั้ง Python packages
- สร้างไดเรกทอรีที่จำเป็น
- ตั้งค่าไฟล์คอนฟิกเริ่มต้น
- รัน Docker containers สำหรับ InfluxDB, Grafana และ n8n
- ตั้งค่า systemd service

4. หลังจากการติดตั้งเสร็จสิ้น ให้แก้ไขไฟล์การตั้งค่า:

```bash
nano config/settings.json
```

ตรวจสอบให้แน่ใจว่าคุณเพิ่ม OpenAI API key และ Discord webhook URL (ถ้าต้องการ)

## การติดตั้งด้วยตนเอง

หากคุณต้องการมีการควบคุมมากขึ้นเกี่ยวกับกระบวนการติดตั้ง คุณสามารถทำตามขั้นตอนเหล่านี้:

### 1. ติดตั้ง dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip lm-sensors docker.io docker-compose
```

### 2. ตั้งค่า lm-sensors

```bash
sudo sensors-detect --auto
```

### 3. โคลนโปรเจค

```bash
git clone https://github.com/diswarin/Ubuntu-Health-Monitor.git
cd Ubuntu-Health-Monitor
```

### 4. ติดตั้ง Python packages

```bash
pip3 install -r requirements.txt
```

### 5. สร้างและแก้ไขไฟล์คอนฟิก

```bash
mkdir -p config logs prompts
cp config/settings.json.example config/settings.json
cp config/thresholds.json.example config/thresholds.json
```

แก้ไข `config/settings.json` เพื่อเพิ่ม OpenAI API key และการตั้งค่าอื่นๆ

### 6. รัน Docker containers

```bash
docker-compose up -d
```

### 7. ตั้งค่า systemd service (ถ้าต้องการ)

```bash
sudo cp systemd/ubuntu-health-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ubuntu-health-monitor
sudo systemctl start ubuntu-health-monitor
```

## การตรวจสอบการติดตั้ง

หลังจากติดตั้งเสร็จ คุณสามารถตรวจสอบว่าทุกอย่างทำงานได้อย่างถูกต้องโดย:

1. ตรวจสอบสถานะของ service:

```bash
sudo systemctl status ubuntu-health-monitor
```

2. ทดสอบ API:

```bash
python3 scripts/test_api.py
```

3. เข้าถึง Grafana dashboard:

เปิดเบราว์เซอร์และไปที่ `http://your-server-ip:3000`
ล็อกอินด้วย username `admin` และ password `admin`

4. ตรวจสอบ InfluxDB:

เปิดเบราว์เซอร์และไปที่ `http://your-server-ip:8086`
ล็อกอินด้วย username `admin` และ password `adminpassword`

5. ตรวจสอบ n8n:

เปิดเบราว์เซอร์และไปที่ `http://your-server-ip:5678`

## การแก้ไขปัญหา

หากคุณพบปัญหาระหว่างการติดตั้ง โปรดตรวจสอบไฟล์บันทึกต่อไปนี้:

- API logs: `logs/api.log`
- System service logs: `sudo journalctl -u ubuntu-health-monitor`
- Docker container logs: `docker-compose logs`

สำหรับคำแนะนำเพิ่มเติมในการแก้ไขปัญหา โปรดดูที่ [Troubleshooting Guide](troubleshooting.md)
