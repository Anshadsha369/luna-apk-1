"""
Smart Home Control - IoT devices, lights, fans, AC, appliances.
Uses MQTT for local IoT or web APIs for cloud devices.
"""

import json
import socket
import threading


class SmartHomeControl:
    def __init__(self):
        self.devices = {}
        self._load_devices()

    def _load_devices(self):
        import json
        from pathlib import Path
        config = Path.home() / ".luna_memory" / "smarthome.json"
        if config.exists():
            try:
                self.devices = json.loads(config.read_text())
            except Exception:
                self.devices = {}

    def _save_devices(self):
        from pathlib import Path
        config = Path.home() / ".luna_memory" / "smarthome.json"
        config.parent.mkdir(exist_ok=True)
        config.write_text(json.dumps(self.devices, indent=2))

    def add_device(self, name, device_type, protocol, address):
        self.devices[name] = {
            "type": device_type,
            "protocol": protocol,
            "address": address,
            "state": "unknown",
        }
        self._save_devices()
        return f"Added {name}"

    def remove_device(self, name):
        if name in self.devices:
            del self.devices[name]
            self._save_devices()
            return f"Removed {name}"
        return f"{name} not found"

    def list_devices(self):
        if not self.devices:
            return "No smart home devices configured."
        return [f"{n}: {d['type']} ({d['state']})" for n, d in self.devices.items()]

    def control(self, device_name, command):
        if device_name not in self.devices:
            # Try fuzzy match
            matches = [n for n in self.devices if device_name.lower() in n.lower()]
            if matches:
                device_name = matches[0]
            else:
                return f"Device '{device_name}' not found"

        device = self.devices[device_name]
        protocol = device.get("protocol", "")

        if protocol == "mqtt":
            return self._mqtt_control(device, command)
        elif protocol == "http":
            return self._http_control(device, command)
        elif protocol == "wled":
            return self._wled_control(device, command)
        elif protocol == "tasmota":
            return self._tasmota_control(device, command)
        else:
            return f"Cannot control {device_name}: unknown protocol {protocol}"

    def _mqtt_control(self, device, command):
        try:
            import paho.mqtt.publish as publish
            topic = device.get("topic", f"home/{device['type']}/{device['name']}")
            payload = "ON" if command in ["on", "true", "1"] else "OFF"
            publish.single(topic, payload, hostname=device.get("broker", "localhost"))
            device["state"] = "on" if payload == "ON" else "off"
            self._save_devices()
            return f"{device['name']} turned {command}"
        except ImportError:
            return "MQTT requires paho-mqtt: pip install paho-mqtt"
        except Exception as e:
            return f"MQTT failed: {e}"

    def _http_control(self, device, command):
        try:
            import requests
            url = device["address"]
            payload = {"state": command}
            r = requests.post(url, json=payload, timeout=5)
            if r.ok:
                device["state"] = command
                self._save_devices()
                return f"{device['name']} turned {command}"
            return f"HTTP control failed: {r.status_code}"
        except Exception as e:
            return f"HTTP error: {e}"

    def _wled_control(self, device, command):
        try:
            import requests
            ip = device["address"]
            if command in ["on", "off"]:
                r = requests.get(f"http://{ip}/win&{(1 if command == 'on' else 0)}", timeout=3)
            elif command.startswith("color") or command.startswith("#"):
                color = command.lstrip("color").strip().lstrip("#")
                r = requests.get(f"http://{ip}/win&COL={color}", timeout=3)
            elif command.startswith("brightness"):
                bri = command.split()[-1]
                r = requests.get(f"http://{ip}/win&A={bri}", timeout=3)
            else:
                return f"Unknown WLED command: {command}"
            device["state"] = command
            self._save_devices()
            return f"WLED {device['name']}: {command}"
        except Exception as e:
            return f"WLED error: {e}"

    def _tasmota_control(self, device, command):
        try:
            import requests
            ip = device["address"]
            power = "1" if command in ["on", "true"] else "0"
            r = requests.get(f"http://{ip}/cm?cmnd=Power%20{power}", timeout=3)
            if r.ok:
                device["state"] = command
                self._save_devices()
                return f"Tasmota {device['name']}: {command}"
            return f"Tasmota error: {r.status_code}"
        except Exception as e:
            return f"Tasmota error: {e}"

    def toggle(self, device_name):
        device = self.devices.get(device_name)
        if not device:
            return f"Device '{device_name}' not found"
        new_state = "off" if device.get("state") == "on" else "on"
        return self.control(device_name, new_state)

    def group_control(self, group_name, command):
        matched = [(n, d) for n, d in self.devices.items()
                   if d.get("type", "").lower() == group_name.lower()]
        if not matched:
            matched = [(n, d) for n, d in self.devices.items()
                       if group_name.lower() in n.lower()]
        if not matched:
            return f"No devices matching '{group_name}'"
        results = []
        for name, _ in matched:
            r = self.control(name, command)
            results.append(f"{name}: {r}")
        return "\n".join(results)

    def discover(self):
        results = []
        for port, name in [(80, "HTTP"), (1883, "MQTT"), (554, "RTSP")]:
            for ip in self._local_ips():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((ip, port)) == 0:
                    results.append(f"{ip}:{port} ({name})")
                sock.close()
        return results or "No devices discovered"

    def _local_ips(self):
        ips = []
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None):
                if info[0] == socket.AF_INET:
                    ip = info[4][0]
                    if ip.startswith("192.168.") or ip.startswith("10."):
                        base = ".".join(ip.split(".")[:3])
                        for i in range(1, 255):
                            ips.append(f"{base}.{i}")
                        break
        except Exception:
            pass
        return ips[:50]
