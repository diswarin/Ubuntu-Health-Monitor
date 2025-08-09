#!/bin/bash

# Ubuntu Health Monitor - Installation Script
# This script installs and configures Ubuntu Health Monitor

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Ubuntu Health Monitor - Installation${NC}"
echo -e "${GREEN}====================================${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Installing required system packages...${NC}"
apt-get update
apt-get install -y python3 python3-pip lm-sensors docker.io docker-compose

# Install lm-sensors
echo -e "${YELLOW}Configuring lm-sensors...${NC}"
yes | sensors-detect

echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r $PROJECT_DIR/requirements.txt

echo -e "${YELLOW}Creating configuration files...${NC}"
mkdir -p $PROJECT_DIR/config
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/prompts

# Copy example config files if they don't exist
if [ ! -f "$PROJECT_DIR/config/settings.json" ]; then
    cp $PROJECT_DIR/config/settings.json.example $PROJECT_DIR/config/settings.json
    echo -e "${YELLOW}Created settings.json from example. Please edit this file to add your API keys.${NC}"
fi

if [ ! -f "$PROJECT_DIR/config/thresholds.json" ]; then
    cp $PROJECT_DIR/config/thresholds.json.example $PROJECT_DIR/config/thresholds.json
    echo -e "${YELLOW}Created thresholds.json from example.${NC}"
fi

echo -e "${YELLOW}Setting up Docker containers...${NC}"
cd $PROJECT_DIR
docker-compose up -d

echo -e "${YELLOW}Setting up systemd service...${NC}"
cp $PROJECT_DIR/systemd/ubuntu-health-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ubuntu-health-monitor
systemctl start ubuntu-health-monitor

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}The following services are now running:${NC}"
echo -e "1. Ubuntu Health Monitor API: http://localhost:5000"
echo -e "2. Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo -e "3. InfluxDB: http://localhost:8086 (admin/adminpassword)"
echo -e "4. n8n Workflows: http://localhost:5678"
echo -e "${YELLOW}Don't forget to edit config/settings.json to add your OpenAI API key and Discord webhook URL${NC}"
