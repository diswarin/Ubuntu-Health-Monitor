from flask import Flask, jsonify
import psutil
import platform
import datetime
import socket
import os

app = Flask(__name__)

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
    
    # Return all info as JSON
    return jsonify({
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
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
