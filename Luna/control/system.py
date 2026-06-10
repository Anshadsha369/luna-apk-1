"""
System Control - device settings, power, display, sound.
"""

import psutil
import os
import time
from datetime import datetime


class SystemControl:
    def get_system_info(self):
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot
        return {
            "cpu": f"{cpu}%",
            "memory": f"{mem.percent}% ({mem.used // 10**9}GB/{mem.total // 10**9}GB)",
            "disk": f"{disk.percent}% free",
            "uptime": str(uptime).split('.')[0],
            "processes": len(psutil.pids()),
        }

    def get_battery(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "plugged in" if battery.power_plugged else "on battery"
                return f"{battery.percent}% ({plugged})"
            return "No battery detected"
        except Exception:
            return "Unknown"

    def list_processes(self, limit=20):
        procs = []
        for p in sorted(psutil.process_iter(['pid', 'name', 'memory_percent']),
                        key=lambda x: x.info['memory_percent'] or 0, reverse=True)[:limit]:
            try:
                procs.append(f"{p.info['name']} ({p.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return procs

    def get_network(self):
        addrs = psutil.net_if_addrs()
        info = {}
        for iface, addr_list in addrs.items():
            for addr in addr_list:
                if addr.family == 2:
                    info[iface] = {"ip": addr.address, "netmask": addr.netmask}
        return info

    def get_storage(self):
        parts = psutil.disk_partitions()
        info = {}
        for p in parts:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                info[p.device] = {
                    "mount": p.mountpoint,
                    "total": f"{usage.total // 10**9}GB",
                    "used": f"{usage.used // 10**9}GB",
                    "free": f"{usage.free // 10**9}GB",
                    "percent": f"{usage.percent}%",
                }
            except Exception:
                continue
        return info

    def get_sensors(self):
        temps = psutil.sensors_temperatures()
        fans = psutil.sensors_fans()
        return {
            "temperatures": {k: [f"{s.current}°C" for s in v] for k, v in temps.items()},
            "fans": {k: [f"{s.current} RPM" for s in v] for k, v in fans.items()},
        }
