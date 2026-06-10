"""
Complete Phone Control - SMS, calls, contacts, files, settings.
"""

from kivy.utils import platform

IS_ANDROID = platform == 'android'


class PhoneControl:
    def __init__(self):
        self._android = None
        if IS_ANDROID:
            self._init_android()

    def _init_android(self):
        try:
            from jnius import autoclass
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.Context = autoclass('android.content.Context')
            self.Intent = autoclass('android.content.Intent')
            self.activity = self.PythonActivity.mActivity
            self._initialized = True
        except Exception:
            self._initialized = False

    def available(self):
        return IS_ANDROID and self._initialized

    def send_sms(self, number, message):
        if not self.available():
            return "SMS requires Android"
        try:
            SmsManager = autoclass('android.telephony.SmsManager')
            sms = SmsManager.getDefault()
            sms.sendTextMessage(number, None, message, None, None)
            return f"Message sent to {number}"
        except Exception as e:
            return f"SMS failed: {e}"

    def read_sms(self, limit=10):
        if not self.available():
            return []
        try:
            Uri = autoclass('android.net.Uri')
            cursor = self.activity.getContentResolver().query(
                Uri.parse("content://sms/inbox"), None, None, None, "date DESC")
            msgs = []
            if cursor and cursor.moveToFirst():
                for _ in range(min(limit, cursor.getCount())):
                    msgs.append({
                        "from": cursor.getString(cursor.getColumnIndexOrThrow("address")),
                        "body": cursor.getString(cursor.getColumnIndexOrThrow("body")),
                    })
                    if not cursor.moveToNext():
                        break
            cursor.close()
            return msgs
        except Exception:
            return []

    def get_contacts(self):
        if not self.available():
            return []
        try:
            Uri = autoclass('android.net.Uri')
            cursor = self.activity.getContentResolver().query(
                Uri.parse("content://contacts/people"), None, None, None, None)
            contacts = []
            if cursor and cursor.moveToFirst():
                while not cursor.isAfterLast():
                    name = cursor.getString(cursor.getColumnIndexOrThrow("display_name"))
                    contacts.append(name)
                    cursor.moveToNext()
            cursor.close()
            return contacts
        except Exception:
            return []

    def call(self, number):
        if not self.available():
            return "Calls require Android"
        try:
            uri = autoclass('android.net.Uri').parse(f"tel:{number}")
            intent = self.Intent(self.Intent.ACTION_CALL, uri)
            self.activity.startActivity(intent)
            return f"Calling {number}"
        except Exception as e:
            return f"Call failed: {e}"

    def open_app(self, package):
        if not self.available():
            return "App launch requires Android"
        try:
            intent = self.activity.getPackageManager().getLaunchIntentForPackage(package)
            if intent:
                self.activity.startActivity(intent)
                return f"Opened app"
            return "App not found"
        except Exception as e:
            return f"Failed: {e}"

    def get_battery(self):
        if not self.available():
            return -1
        try:
            BatteryManager = autoclass('android.os.BatteryManager')
            intent = self.activity.registerReceiver(None,
                self.Intent(BatteryManager.ACTION_BATTERY_CHANGED))
            level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            return int(level * 100 / scale) if scale > 0 else level
        except Exception:
            return -1

    def is_charging(self):
        if not self.available():
            return False
        try:
            BatteryManager = autoclass('android.os.BatteryManager')
            intent = self.activity.registerReceiver(None,
                self.Intent(BatteryManager.ACTION_BATTERY_CHANGED))
            status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
            return status == BatteryManager.BATTERY_STATUS_CHARGING
        except Exception:
            return False

    def toggle_wifi(self, enable=True):
        if not self.available():
            return False
        try:
            WifiManager = autoclass('android.net.wifi.WifiManager')
            wifi = self.activity.getSystemService(self.Context.WIFI_SERVICE)
            wifi = WifiManager(wifi)
            wifi.setWifiEnabled(enable)
            return True
        except Exception:
            return False

    def toggle_bluetooth(self, enable=True):
        if not self.available():
            return False
        try:
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            if adapter:
                if enable:
                    adapter.enable()
                else:
                    adapter.disable()
                return True
            return False
        except Exception:
            return False

    def set_brightness(self, level):
        if not self.available():
            return False
        try:
            from jnius import autoclass
            level = max(0, min(255, int(level * 255 / 100)))
            self.activity.getContentResolver().putInt(
                autoclass('android.provider.Settings$System').SCREEN_BRIGHTNESS, level)
            return True
        except Exception:
            return False

    def take_screenshot(self):
        if not self.available():
            return False
        try:
            import os
            path = f"/sdcard/Pictures/Luna/screenshot_{int(time.time())}.png"
            os.makedirs("/sdcard/Pictures/Luna", exist_ok=True)
            view = self.activity.getWindow().getDecorView().getRootView()
            view.setDrawingCacheEnabled(True)
            bitmap = view.getDrawingCache()
            # Save bitmap (requires Java reflection)
            return path
        except Exception:
            return False

    def list_installed_apps(self):
        if not self.available():
            return []
        try:
            packages = self.activity.getPackageManager().getInstalledApplications(0)
            return [pkg.loadLabel(self.activity.getPackageManager())
                    for pkg in packages.toArray()[:100]]
        except Exception:
            return []
