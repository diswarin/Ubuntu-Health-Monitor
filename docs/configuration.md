# คู่มือการตั้งค่า Ubuntu Health Monitor

เอกสารนี้จะแนะนำวิธีการตั้งค่า Ubuntu Health Monitor ให้เหมาะกับความต้องการของคุณ

## การตั้งค่าหลัก (config/settings.json)

ไฟล์ `config/settings.json` ประกอบด้วยการตั้งค่าหลักของระบบ:

```json
{
  "openai": {
    "api_key": "your-api-key-here",
    "model": "gpt-4"
  },
  "discord": {
    "webhook_url": "your-discord-webhook-url-here"
  },
  "influxdb": {
    "url": "http://localhost:8086",
    "token": "my-token",
    "org": "my-org",
    "bucket": "system_metrics"
  }
}
```

### การตั้งค่า OpenAI

- `api_key`: API key ของ OpenAI ของคุณ สามารถรับได้จาก [OpenAI Platform](https://platform.openai.com/account/api-keys)
- `model`: โมเดลที่จะใช้สำหรับการวิเคราะห์ (เช่น "gpt-4", "gpt-3.5-turbo")

### การตั้งค่า Discord

- `webhook_url`: Discord webhook URL สำหรับการส่งการแจ้งเตือน สามารถสร้างได้ในการตั้งค่าช่องของ Discord ของคุณ

### การตั้งค่า InfluxDB

- `url`: URL ของ InfluxDB server
- `token`: Token สำหรับการเข้าถึง InfluxDB
- `org`: ชื่อองค์กรใน InfluxDB
- `bucket`: ชื่อ bucket ที่จะใช้เก็บข้อมูล

## การตั้งค่า Thresholds (config/thresholds.json)

ไฟล์ `config/thresholds.json` กำหนดค่าขีดจำกัดสำหรับการแจ้งเตือน:

```json
{
  "cpu_percent": 80,
  "memory_percent": 85,
  "disk_percent": 90,
  "temperature": 70
}
```

- `cpu_percent`: เปอร์เซ็นต์การใช้งาน CPU ที่จะทริกเกอร์การแจ้งเตือน
- `memory_percent`: เปอร์เซ็นต์การใช้งาน Memory ที่จะทริกเกอร์การแจ้งเตือน
- `disk_percent`: เปอร์เซ็นต์การใช้งาน Disk ที่จะทริกเกอร์การแจ้งเตือน
- `temperature`: อุณหภูมิในหน่วย Celsius ที่จะทริกเกอร์การแจ้งเตือน

## การปรับแต่ง Prompts (prompts/system_summary_prompt.txt)

ไฟล์ `prompts/system_summary_prompt.txt` ประกอบด้วย prompt ที่ส่งไปยัง OpenAI API สำหรับการวิเคราะห์ระบบ คุณสามารถปรับแต่งไฟล์นี้เพื่อปรับเปลี่ยนวิธีที่ AI วิเคราะห์และตอบสนองต่อข้อมูลระบบของคุณ

## การตั้งค่า Docker (docker-compose.yml)

ไฟล์ `docker-compose.yml` กำหนดการตั้งค่าสำหรับ Docker containers:

### InfluxDB

```yaml
influxdb:
  image: influxdb:2.7
  container_name: influxdb
  ports:
    - "8086:8086"
  volumes:
    - ./influxdb-data:/var/lib/influxdb2
  environment:
    - DOCKER_INFLUXDB_INIT_MODE=setup
    - DOCKER_INFLUXDB_INIT_USERNAME=admin
    - DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword
    - DOCKER_INFLUXDB_INIT_ORG=my-org
    - DOCKER_INFLUXDB_INIT_BUCKET=system_metrics
    - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-token
  restart: unless-stopped
```

คุณสามารถปรับเปลี่ยนชื่อผู้ใช้, รหัสผ่าน, ชื่อองค์กร, ชื่อ bucket และ token ได้ตามต้องการ ตรวจสอบให้แน่ใจว่าการเปลี่ยนแปลงเหล่านี้สอดคล้องกับการตั้งค่าใน `config/settings.json`

### Grafana

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: grafana
  ports:
    - "3000:3000"
  volumes:
    - ./grafana-data:/var/lib/grafana
    - ./dashboards:/etc/grafana/provisioning/dashboards
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
  depends_on:
    - influxdb
  restart: unless-stopped
```

คุณสามารถปรับเปลี่ยนชื่อผู้ใช้, รหัสผ่าน และ plugins ที่ติดตั้งได้

### n8n

```yaml
n8n:
  image: n8nio/n8n:latest
  container_name: n8n
  ports:
    - "5678:5678"
  volumes:
    - ./n8n-data:/home/node/.n8n
    - ./workflows:/home/node/.n8n/workflows
  environment:
    - N8N_HOST=localhost
    - N8N_PORT=5678
    - N8N_PROTOCOL=http
    - NODE_ENV=production
    - WEBHOOK_URL=http://localhost:5678/
    - GENERIC_TIMEZONE=Asia/Bangkok
  restart: unless-stopped
```

คุณสามารถปรับเปลี่ยน host, port และ timezone ได้

## การตั้งค่า systemd Service (systemd/ubuntu-health-monitor.service)

ไฟล์ `systemd/ubuntu-health-monitor.service` กำหนดการตั้งค่าสำหรับ systemd service:

```ini
[Unit]
Description=Ubuntu Health Monitor
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Ubuntu-Health-Monitor
ExecStart=/usr/bin/python3 /home/ubuntu/Ubuntu-Health-Monitor/app.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=ubuntu-health-monitor
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

แก้ไข `User` และ `WorkingDirectory` ให้ตรงกับชื่อผู้ใช้และตำแหน่งของโปรเจคของคุณ

## การตั้งค่า Grafana

1. เข้าถึง Grafana dashboard ที่ `http://your-server-ip:3000`
2. ล็อกอินด้วยชื่อผู้ใช้และรหัสผ่านที่คุณกำหนดใน docker-compose.yml
3. ไปที่ Configuration > Data Sources > Add data source
4. เลือก InfluxDB
5. ใส่ URL: `http://influxdb:8086`
6. เลือก InfluxQL หรือ Flux ตามต้องการ
7. สำหรับ Flux, ใส่ Organization, Token และ Default Bucket ที่ตรงกับการตั้งค่าของคุณ
8. คลิก "Save & Test" เพื่อยืนยันการเชื่อมต่อ
9. นำเข้า dashboard จากไฟล์ `dashboards/system_overview.json`

## การตั้งค่า n8n

1. เข้าถึง n8n dashboard ที่ `http://your-server-ip:5678`
2. ไปที่ Settings > Import From File
3. เลือกไฟล์ `workflows/server_monitor_workflow.json`
4. หลังจากนำเข้า workflow, คลิกที่ workflow เพื่อแก้ไข
5. ตั้งค่า credentials สำหรับ Discord webhook
6. ตรวจสอบและแก้ไข URL ของ HTTP Request nodes ให้ชี้ไปยัง API ของคุณ
7. บันทึกและเปิดใช้งาน workflow
