from flask import Flask, jsonify, request
import psutil
import platform
import datetime
import socket
import os
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

# Load configuration
with open('config/settings.json', 'r') as f:
    config = json.load(f)

# InfluxDB configuration
INFLUXDB_URL = config.get('influxdb_url', 'http://localhost:8086')
INFLUXDB_TOKEN = config.get('influxdb_token', 'YourSecureToken123')
INFLUXDB_ORG = config.get('influxdb_org', 'ubuntu-monitor')
INFLUXDB_BUCKET = config.get('influxdb_bucket', 'system-metrics')

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    # CPU info
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    
    # Memory info
    memory = psutil.virtual_memory()
    
    # Disk info
    disk = psutil.disk_usage('/')
    
    # Network info
    net_io = psutil.net_io_counters()
    
    # System uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    
    # Load average
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    # Running processes
    process_count = len(list(psutil.process_iter()))
    
    # Basic system info
    system_info = {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor()
    }
    
    # Create response data
    response_data = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'system': system_info,
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else None,
            'load_avg_1min': load_avg[0],
            'load_avg_5min': load_avg[1],
            'load_avg_15min': load_avg[2]
        },
        'memory': {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent': memory.percent
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': disk.percent
        },
        'network': {
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        },
        'uptime': {
            'days': uptime.days,
            'hours': uptime.seconds // 3600,
            'minutes': (uptime.seconds % 3600) // 60,
            'seconds': uptime.seconds % 60,
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'processes': {
            'count': process_count
        }
    }
    
    # Write data to InfluxDB if enabled in config
    if config.get('influxdb_enabled', True):
        try:
            # Create a point for CPU metrics
            point = Point("system_metrics") \
                .tag("host", system_info['hostname']) \
                .field("cpu_percent", cpu_percent) \
                .field("memory_percent", memory.percent) \
                .field("disk_percent", disk.percent) \
                .field("load_avg_1min", load_avg[0]) \
                .field("process_count", process_count) \
                .time(datetime.datetime.utcnow())
            
            # Write the point to InfluxDB
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            
            # Log successful write to InfluxDB
            app.logger.info(f"Data written to InfluxDB at {datetime.datetime.now()}")
        except Exception as e:
            app.logger.error(f"Error writing to InfluxDB: {str(e)}")
    
    # Return response data as JSON
    return jsonify(response_data)

@app.route('/api/metrics/history', methods=['GET'])
def get_metrics_history():
    # Get query parameters
    metric = request.args.get('metric', 'cpu_percent')
    duration = request.args.get('duration', '1h')
    
    # Query InfluxDB for historical data
    query_api = influxdb_client.query_api()
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{duration})
        |> filter(fn: (r) => r._measurement == "system_metrics")
        |> filter(fn: (r) => r._field == "{metric}")
    '''
    
    try:
        result = query_api.query(org=INFLUXDB_ORG, query=query)
        
        # Process the results
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    'time': record.get_time().strftime('%Y-%m-%d %H:%M:%S'),
                    'value': record.get_value()
                })
        
        return jsonify({
            'metric': metric,
            'duration': duration,
            'data_points': data_points
        })
    except Exception as e:
        app.logger.error(f"Error querying InfluxDB: {str(e)}")
        return jsonify({
            'error': f"Failed to retrieve historical data: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Create directory for logs if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up logging
    import logging
    from logging.handlers import RotatingFileHandler
    
    handler = RotatingFileHandler('logs/api.log', maxBytes=10000000, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Ubuntu Health Monitor starting up')
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)